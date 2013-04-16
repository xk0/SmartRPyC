"""
Base objects for the RPC
"""

import logging

import zmq
import msgpack

from smartrpyc.utils import lazy_property

__all__ = ['MethodsRegister', 'Server', 'Request', 'ServerMiddlewareBase']

logger = logging.getLogger(__name__)


class MethodsRegister(object):
    """
    Register for methods to be exposed via RPC.
    Mostly a wrapper around a dict.

    Usage::

        methods = MethodsRegister()

        @methods.register
        def my_method(request, arg1, arg2):
            pass

        @methods.register(name='method2')
        def my_other_method(request, arg1=123, arg2=None):
            pass

        methods.register(func=func, name='test')

        # then pass methods to the Server() constructor
    """
    def __init__(self):
        self._methods = {}

    def register(self, func=None, name=None):
        """
        Refer to class docstring

        :params func: Callable to register
        :params name: Basestring to use as reference
            name for `func`
        """

        # If name is None we'll get the name from the
        # function itself.
        name = name or callable(func) and func.__name__

        def decorator(func):
            self.store(name, func)
            return func

        # If func is not None, it means the method
        # has been used either as a simple decorator
        # or as a plain method. The function will be
        # registered by calling decorator, otherwise,
        # decorator will be returned.
        return func and decorator(func) or decorator

    def store(self, name, function):
        """
        Method used to finally register a
        function.

        :params name:
            Functions lookup name
        :params function:
            Callable function
        """
        if not isinstance(name, basestring) and not callable(function):
            # If we get here, most likely, the user has passed
            # a non callable function. See unittest for a clearer
            # example.
            raise ValueError("Unsupported arguments to register: "
                             "{} and {}".format(name, function))
        self._methods[name] = function

    def lookup(self, method):
        return self._methods[method]


class Request(object):
    """Wrapper for requests from the RPC"""

    def __init__(self, raw):
        self.raw = raw

    @property
    def method(self):
        return self.raw['m']

    @property
    def args(self):
        return self.raw.get('a') or ()

    @property
    def kwargs(self):
        return self.raw.get('k') or {}


class Server(object):
    request_class = Request

    def __init__(self, methods=None):
        """
        Constructor for the RPC Server class

        :param methods:
            Methods to be exposed via RPC. Usually a ``MethodsRegister``
            instance, but this is not mandatory.
            It has to have a ``lookup(name)`` method, returning
            the specified method, or raising an exception if the method
            was not found.
        """
        self.methods = methods
        if self.methods is None:
            self.methods = MethodsRegister()

        self.middleware = []  # Middleware chain

    @lazy_property
    def socket(self):
        context = zmq.Context()
        return context.socket(zmq.REP)

    def bind(self, addresses):
        """
        Bind the server socket to an address (or a list of)

        :params addresses:
            A (list of) address(es) to which to bind the server.
        """
        if not isinstance(addresses, (list, tuple)):
            addresses = [addresses]
        for addr in addresses:
            self.socket.bind(addr)

    def run(self):
        """Start the server listening loop"""
        while True:
            self.run_once()

    def run_once(self):
        """Run once: process a request and send a response"""
        message_raw = self.socket.recv()
        message = self.request_class(
            msgpack.unpackb(message_raw, encoding='utf-8'))
        response = self._process_request(message)
        self.socket.send(msgpack.packb(response, encoding='utf-8'))

    def _process_request(self, request):
        """Process a received request"""

        try:
            method = self.methods.lookup(request.method)
        except KeyError:
            msg = 'No such method: {}'.format(request.method)
            logger.error(msg)
            return self._exception_message(msg)

        try:
            self._exec_pre_middleware(request, method)
        except Exception, e:
            logger.exception('Exception during execution of PRE middleware')
            return self._exception_message(e)

        try:
            response = method(request, *request.args, **request.kwargs)
        except Exception, e:
            logger.exception('Exception during execution of request')
            response = None
            exception = e
        else:
            exception = None

        try:
            response = self._exec_post_middleware(
                request, method, response, exception)
        except Exception, e:
            logger.exception('Exception during execution of POST middleware')
            return self._exception_message(e)

        if exception is not None:
            return self._exception_message(exception)
        else:
            return {'r': response}

    def _exception_message(self, exception):
        return {
            'e': type(exception).__name__,
            'e_msg': str(exception),
        }

    def _exec_pre_middleware(self, request, method):
        for mw in self.middleware:
            if hasattr(mw, 'pre'):
                mw.pre(request, method)

    def _exec_post_middleware(self, request, method, response, exception):
        for mw in reversed(self.middleware):
            if hasattr(mw, 'post'):
                retval = mw.post(request, method, response, exception)
                if retval is not None:
                    response = retval
        return response


class ServerMiddlewareBase(object):
    """
    Base class for server middleware.
    (mostly a reminder for methods signatures, subclassing from
    this is not mandatory).
    """

    def pre(self, request, method):
        pass

    def post(self, request, method, response, exception):
        pass
