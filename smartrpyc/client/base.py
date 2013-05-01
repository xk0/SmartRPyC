"""
SmartRPC client
"""

import uuid
import zmq

from smartrpyc.utils import lazy_property
from smartrpyc.utils.serialization import MsgPackSerializer

__all__ = ['Client', 'IntrospectableClient', 'RemoteException',
           'ClientMiddlewareBase']


class RemoteException(Exception):
    """
    Wrapper around a remote exception.
    Ideally, this should fake to be an instance of the remote
    exception too, but that's not the case yet.. :(

    Eg:

    >>> exc = RemoteException('ValueError', 'Invalid value')
    >>> isinstance(exc, RemoteException)
    True
    >>> isinstance(exc, ValueError)
    True
    """

    def __init__(self, exc, msg):
        self.message = msg
        self.original_exc = exc

    def __str__(self):
        return "{0}: {1}".format(self.original_exc, self.message)

    def __repr__(self):
        return "<RemoteException: {0!r}>".format(str(self))


class Client(object):
    packer = MsgPackSerializer

    def __init__(self, address=None):
        self._address = address
        self.middleware = []  # Middleware chain

    @lazy_property
    def _socket(self):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        # if self._address is not None:
        socket.connect(self._address)
        return socket

    def _do_request(self, method, args, kwargs):
        request = self._prepare_request({
            'i': str(uuid.uuid4()),
            'm': method,
            'a': args,
            'k': kwargs,
        })

        request = self._exec_pre_middleware(request)

        packed = self.packer.packb(request)
        self._socket.send(packed)
        return request

    def _get_response(self, request):
        response = self.packer.unpackb(self._socket.recv())

        response = self._exec_post_middleware(request, response)

        if 'e' in response:
            raise RemoteException(response['e'], response.get('e_msg'))
        return response['r']

    def _prepare_request(self, request):
        return request

    def __getattr__(self, item):
        if item.startswith('_'):
            raise AttributeError(item)

        server = self

        class method_proxy(object):
            def __call__(self, *a, **kw):
                request = server._do_request(item, a, kw)
                return server._get_response(request)

            @lazy_property
            def __doc__(self):
                request = server._do_request('doc', (item,), {})
                return server._get_response(request)

        # def method_proxy(*a, **kw):
        #     request = self._do_request(item, a, kw)
        #     return self._get_response(request)

        return method_proxy()

    def _exec_pre_middleware(self, request):
        for mw in self.middleware:
            if hasattr(mw, 'pre'):
                retval = mw.pre(request)
                if retval is not None:
                    request = retval
        return request

    def _exec_post_middleware(self, request, response):
        for mw in reversed(self.middleware):
            if hasattr(mw, 'post'):
                retval = mw.post(request, response)
                if retval is not None:
                    response = retval
        return response


class IntrospectableClient(Client):
    def __dir__(self):
        methods = dir(super(IntrospectableClient, self))
        methods += self.dir()
        return methods


class ClientMiddlewareBase(object):
    """
    Base class for client middleware.
    (mostly a reminder for methods signatures, subclassing from
    this is not mandatory).
    """

    def pre(self, request):
        pass

    def post(self, request, response):
        pass
