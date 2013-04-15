import zmq

from smartrpyc import utils
from smartrpyc.client import base, exceptions


class Lazy(base.Client):
    def __init__(self, retries=3, timeout=1000, **kwargs):
        self._retries = retries
        self._timeout = timeout
        super(Lazy, self).__init__(**kwargs)

    @utils.lazy_property
    def _poller(self):
        poller = zmq.Poller()
        poller.register(self._socket, zmq.POLLIN)
        return poller

    def _get_response(self, request, retries=None):
        if not retries is None and retries <= 0:
            self._socket.setsockopt(zmq.LINGER, 0)
            self._socket.close()
            self._poller.unregister(self._socket)
            raise exceptions.ServerUnavailable("")

        socks = dict(self._poller.poll(self._timeout))
        if socks.get(self._socket) == zmq.POLLIN:
            return super(Lazy, self)._get_response(request)

        retries = (retries or self._retries) - 1
        return self._get_response(request, retries=retries)
