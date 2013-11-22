"""
Base objects for the RPC
"""

from collections import defaultdict
import logging

import zmq

from smartrpyc.utils import lazy_property
from smartrpyc.utils.serialization import MsgPackSerializer
from .register import MethodsRegister
from .exceptions import DirectResponse, SetMethod

__all__ = ['Server', 'Request']

logger = logging.getLogger(__name__)


class Request(object):
    """Wrapper for requests from the RPC"""

    server = None

    def __init__(self, raw):
        """
        :param raw: The (unpacked) content of the request
        """
        self.raw = raw

    @property
    def id(self):
        """Id of the request"""
        return self.raw['i']

    @property
    def route(self):
        """Route of the request"""
        return self.raw.get('r', '')

    @property
    def method(self):
        """Name of the method to be called"""
        return self.raw['m']

    @property
    def args(self):
        """Positional arguments for the called method"""
        return self.raw.get('a') or ()

    @property
    def kwargs(self):
        """Keyword arguments for the called method"""
        return self.raw.get('k') or {}


class Server(object):
    request_class = Request
    packer = MsgPackSerializer
    middleware = None

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
        self._routes = defaultdict(MethodsRegister)
        if methods is not None:
            self.methods = methods
        self.middleware = []  # Middleware chain

    @property
    def methods(self):
        return self.routes['']

    @methods.setter
    def methods(self, value):
        assert isinstance(value, MethodsRegister)
        self.routes[''] = value

    @property
    def routes(self):
        ## Prevent direct assignment

        ## DAFUQ??
        # if not all(isinstance(v, MethodsRegister)
        #            for k, v in self._routes.iteritems()):
        #     import pdb
        #     pdb.set_trace()

        return self._routes

    @lazy_property
    def socket(self):
        context = zmq.Context()
        return context.socket(zmq.REP)

    def bind(self, addresses):
        """
        Bind the server socket to an address (or a list of)

        **Beware!** Only ``.bind()`` or ``.connect()`` may be called on
        a given server instance!

        :params addresses:
            A (list of) address(es) to which to bind the server.
        """
        if not isinstance(addresses, (list, tuple)):
            addresses = [addresses]
        for addr in addresses:
            self.socket.bind(addr)

    def connect(self, addresses):
        """
        Connect the server socket to an address (or a list of)

        **Beware!** Only ``.bind()`` or ``.connect()`` may be called on
        a given server instance!

        :params addresses:
            A (list of) address(es) to which to connect the server.
        """
        if not isinstance(addresses, (list, tuple)):
            addresses = [addresses]
        for addr in addresses:
            self.socket.connect(addr)

    def run(self):
        """Start the server listening loop"""
        while True:
            self.run_once()

    def run_once(self):
        """Run once: process a request and send a response"""
        message_raw = self.socket.recv()
        try:
            request = self.request_class(self.packer.unpackb(message_raw))
            request.server = self
            response = self._process_request(request)
        except Exception, e:
            ## If anything bad happened, send an exception message
            ## to the user.
            ## We need to make damn sure something is sent to the client,
            ## or the request will hang forever..
            ## We might as well want a way to timeout connections, to prevent
            ## hanging at all...
            self.socket.send(
                self.packer.packb(
                    self._exception_message(e)))
        else:
            ## Send the response message to the client
            self.socket.send(self.packer.packb(response))

    def _lookup_method(self, request):
        """Find method to be used for this request"""
        if request.route not in self.routes:
            raise KeyError("No such route: {0!r}".format(request.route))
        route = self.routes[request.route]
        try:
            return route.lookup(request.method)
        except:
            raise KeyError("No such method: {method!r} (route: {route!r})"
                           "".format(route=request.route,
                                     method=request.method))

    def _process_request(self, request):
        """Process a received request"""

        logger.debug("Processing request")

        exception = None
        method = None

        ## Lookup the requested method
        try:
            method = self._lookup_method(request)
        except KeyError, e:
            logger.error(str(e))

            ## We don't terminate here, as a "pre" middleware
            ## might have a solution for this..
            exception = e

        ## Execute all the PRE middleware on the request
        try:
            self._exec_pre_middleware(request, method)

        except DirectResponse, e:
            logger.debug("A PRE middleware requested to send a response now")
            return self._response_message(e.response)

        except SetMethod, e:
            logger.debug("A PRE middleware changed the method to be called")
            method = e.method
            exception = None  # Clear exceptions happened before..

        except Exception, e:
            logger.exception('Exception during execution of "pre" middleware')
            return self._exception_message(e)

        ## If the method is still None, return the current exception
        if method is None:
            if exception is None:
                exception = KeyError("No such method")
            return self._exception_message(exception)

        ## Execute the method
        try:
            response = method(request, *request.args, **request.kwargs)
        except Exception, e:
            logger.exception('Exception during execution of request')
            response = None
            exception = e
        else:
            exception = None

        ## Execute all the POST middleware on request + response
        try:
            response = self._exec_post_middleware(
                request, method, response, exception)
        except DirectResponse, e:
            logger.info(
                'A "post" middleware requested immediate returning '
                'of a response')
            return self._response_message(e.response)
        except Exception, e:
            logger.exception('Exception during execution of "post" middleware')
            ## Exceptions in the POST middleware are fatal..
            return self._exception_message(e)

        ## If there was an exception, return it as a special message
        if exception is not None:
            return self._exception_message(exception)

        ## Return the response message
        return self._response_message(response)

    def _exception_message(self, exception):
        """
        Create a response object indicating an exception occurred.

        :param exception:
            The original exception
        :return:
            An object with the ``e`` (name) and ``e_msg`` (message) keys.
        """
        return {
            'e': type(exception).__name__,
            'e_msg': str(exception),
        }

    def _response_message(self, response):
        """
        Create a "normal" response message.

        The message is simply a dict with an ``r`` key containing
        the result value. This is needed to distinguish between
        return values and exceptions.
        """
        return {'r': response}

    def _exec_pre_middleware(self, request, method):
        """
        Run all the "pre" middleware functions

        :param request: The request being processed
        :param method: The method that will be used to process the request
        """
        for mw in self.middleware:
            if hasattr(mw, 'pre'):
                mw.pre(request, method)

    def _exec_post_middleware(self, request, method, response, exception):
        """
        Run all the "post" middleware functions

        :param request: The original request object
        :param method: The figured out method for the request
        :param response: Response from the method (if any)
        :param exception: Exception raised from the method (if any)
        """
        for mw in reversed(self.middleware):
            if hasattr(mw, 'post'):
                retval = mw.post(request, method, response, exception)
                if retval is not None:
                    response = retval
        return response
