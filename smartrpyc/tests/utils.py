import sys
from multiprocessing import Process

## For Python < 2.7, we need to use unittest2 that contains
## backported functionality introduced only in 2.7
if sys.version_info <= (2, 7):
    try:
        import unittest2 as unittest
    except ImportError:
        import unittest
else:
    import unittest

from smartrpyc import server


class ExampleRpcProcess(Process):

    def __init__(self, methods, addresses=None, middleware=None):
        super(ExampleRpcProcess, self).__init__()
        self._methods = methods
        self._addresses = addresses
        self._middleware = middleware

    def run(self):
        self.rpc = server.Server(self._methods)
        if self._middleware is not None:
            self.rpc.middleware[:] = self._middleware[:]

        self.rpc.bind(self._addresses)
        self.rpc.run()


class FunctionalTest(unittest.TestCase):

    def start_server(self, methods, addresses):
        self.rpc_process = ExampleRpcProcess(methods, addresses)
        self.rpc_process.daemon = True
        self.rpc_process.start()
        return self.rpc_process

    def stop_server(self):
        self.rpc_process.terminate()
        self.rpc_process.join(timeout=3)
