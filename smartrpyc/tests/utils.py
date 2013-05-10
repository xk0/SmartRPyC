"""
Utilities for unittests
"""

# import multiprocessing
import threading
from smartrpyc import server


class ExampleRpcProcess(threading.Thread):
    """Process running a SmartRPyC server"""

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


class TestingServer(object):
    """Context manager to provide a server"""

    def __init__(self, methods, addresses, middleware=None):
        self.methods = methods
        self.addresses = addresses
        self.middleware = middleware

    def __enter__(self):
        self.rpc_process = ExampleRpcProcess(
            self.methods, self.addresses, middleware=self.middleware)
        self.rpc_process.daemon = True
        self.rpc_process.start()
        return self.rpc_process

    def __exit__(self, exc_type, exc_val, exc_tb):
        # self.rpc_process.terminate()
        # self.rpc_process.join(timeout=3)
        ## the thread should terminate when going out of scope..
        pass
