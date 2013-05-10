import pytest
from smartrpyc.server import MethodsRegister
from smartrpyc.client import pirate
from smartrpyc.client import exceptions
from smartrpyc.utils import get_random_ipc_socket
from smartrpyc.tests import utils


class TestLazyClient(object):

    def get_methods(self):
        self.methods = MethodsRegister()

        @self.methods.register
        def hello(request):
            return "world"

        return self.methods

        # self.addr = get_random_ipc_socket()

    def test_server_active(self):
        addr = get_random_ipc_socket()

        with utils.TestingServer(self.get_methods(), addr) as proc:
            proc.join(1)

            # retries 3, timeout 3
            c = pirate.Lazy(address=addr)
            assert 'world' == c.hello()

    def test_server_unavailable(self):
        # retries 3, timeout 3
        addr = get_random_ipc_socket()
        c = pirate.Lazy(retries=1, timeout=0, address=addr)

        with pytest.raises(exceptions.ServerUnavailable):
            c.hello()
