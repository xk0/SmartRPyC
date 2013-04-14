import unittest
from multiprocessing import Process

from smartrpyc import server


class ExampleRpcProcess(Process):
    daemon = True

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
        self.rpc_process.start()
        return self.rpc_process

    def stop_server(self):
        self.rpc_process.terminate()
