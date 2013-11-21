"""
Base objects for the RPC
"""

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
        return self.raw["i"]

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
        request = self.request_class(self.packer.unpackb(message_raw))
        request.server = self
        response = self._process_request(request)
        self.socket.send(self.packer.packb(response))

    def _process_request(self, request):
        """Process a received request"""

        logger.debug("Processing request")

        exception = None
        method = None

        ## Lookup the requested method
        try:
            method = self.methods.lookup(request.method)
        except KeyError:
            msg = 'No such method: {0}'.format(request.method)
            logger.error(msg)
            exception = KeyError(msg)

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
            logger.exception('Exception during execution of PRE middleware')
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
                "A POST middleware requested immediate returning "
                "of a response")
            return self._response_message(e.response)
        except Exception, e:
            logger.exception('Exception during execution of POST middleware')
            return self._exception_message(e)

        ## If there was an exception, return it as a special message
        if exception is not None:
            return self._exception_message(exception)

        ## Return the response message
        return self._response_message(response)

    def _exception_message(self, exception):
        return {
            'e': type(exception).__name__,
            'e_msg': str(exception),
        }

    def _response_message(self, response):
        return {'r': response}

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
