from smartrpyc.server import MethodsRegister
from smartrpyc.client import pirate
from smartrpyc.client import exceptions
from smartrpyc.tests import utils
from smartrpyc.utils import get_random_ipc_socket


class LazyClient(utils.FunctionalTest):

    def setUp(self):
        self.methods = MethodsRegister()

        @self.methods.register
        def hello(request):
            return "world"

        self.addr = get_random_ipc_socket()

    def test_server_active(self):
        proc = self.start_server(self.methods, self.addr)
        proc.join(1)

        # retries 3, timeout 3
        c = pirate.Lazy(address=self.addr)
        self.assertEqual('world', c.hello())
        self.stop_server()

    def test_server_unavailable(self):
        # retries 3, timeout 3
        c = pirate.Lazy(retries=1, timeout=0, address=self.addr)

        with self.assertRaises(exceptions.ServerUnavailable):
            c.hello()
