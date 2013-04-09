"""
SmartRPC client
"""

import msgpack
import zmq

from .utils import lazy_property

__all__ = ['Client', 'RemoteException']


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
        return "{}: {}".format(self.original_exc, self.message)

    def __repr__(self):
        return "<RemoteException: {!r}>".format(str(self))


class Client(object):
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
            'm': method,
            'a': args,
            'k': kwargs,
        })

        request = self._exec_pre_middleware(request)

        packed = msgpack.packb(request, encoding='utf-8')
        self._socket.send(packed)

        response = msgpack.unpackb(self._socket.recv(), encoding='utf-8')

        response = self._exec_post_middleware(request, response)

        if 'e' in response:
            raise RemoteException(response['e'], response.get('e_msg'))
        return response['r']

    def _prepare_request(self, request):
        return request

    def __getattr__(self, item):
        if item.startswith('_'):
            raise AttributeError(item)

        def method_proxy(*a, **kw):
            return self._do_request(item, a, kw)

        return method_proxy

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
