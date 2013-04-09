"""
Base objects for the RPC
"""

import logging

import zmq
import msgpack

from .utils import lazy_property

__all__ = ['MethodsRegister', 'Server', 'Request']

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

        @methods.register('method2')
        def my_other_method(request, arg1=123, arg2=None):
            pass

        # then pass methods to the Server() constructor
    """
    def __init__(self):
        self._methods = {}

    def register(self, name=None, func=None):
        ## Use as plain decorator: @register
        if name is None and func is None:
            def decorator(func):
                self._methods[func.__name__] = func
                return func
            return decorator

        ## Use as register(callable)
        elif hasattr(name, '__call__'):
            self._methods[name.__name__] = name
            return name

        ## Use as register(name, callable) or register(func=callable)
        elif hasattr(func, '__call__'):
            self._methods[name or func.__name__] = func
            return func

        ## Use as decorator: @register(name)
        elif (name is not None) and (func is None):
            def decorator(func):
                self._methods[name] = func
                return func
            return decorator

        ## Wrong use
        raise ValueError(
            "Unsupported arguments to register: {!r} and {!r}"
            "".format(name, func))

    def lookup(self, method):
        return self._methods[method]

    def __call__(self, *args, **kwargs):
        return self.register(*args, **kwargs)


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

    def __init__(self, methods=None, addresses=None):
        """
        Constructor for the RPC Server class

        :param methods:
            Methods to be exposed via RPC. Usually a ``MethodsRegister``
            instance, but this is not mandatory.
            It has to have a ``lookup(name)`` method, returning
            the specified method, or raising an exception if the method
            was not found.
        :param addresses:
            A (list of) address(es) to which to bind the server.
        """
        if methods is None:
            methods = MethodsRegister()
        self.methods = methods
        if addresses is not None:
            self.bind(addresses)
        self.middleware = []  # Middleware chain

    @lazy_property
    def socket(self):
        context = zmq.Context()
        return context.socket(zmq.REP)

    def bind(self, addresses):
        """Bind the server socket to an address (or a list of)"""
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

        method = self.methods.lookup(request.method)

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
