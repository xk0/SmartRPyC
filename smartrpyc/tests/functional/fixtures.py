"""
Fixtures for functional tests
"""

import multiprocessing

import pytest
import zmq

from smartrpyc.server import Server
from smartrpyc.client import Client
from smartrpyc.utils import get_random_ipc_socket

__all__ = ['random_socket', 'simple_server_client',
           'multiroute_server_client', 'simple_server', 'multiroute_server']


class ServerProcessThread(multiprocessing.Process):
    def __init__(self, rpcserver, addresses):
        super(ServerProcessThread, self).__init__()
        self._rpc = rpcserver
        self._addresses = addresses

    def run(self):
        self._rpc.bind(self._addresses)
        self._rpc.run()


class ServerClientPair(object):
    """Context manager to provide a server"""

    def __init__(self, server, client, address):
        self.server = server
        self.client = client
        self.address = address

    def __enter__(self):
        self.server_thread = ServerProcessThread(self.server, self.address)
        self.server_thread.daemon = True  # Should die when orphaned
        self.server_thread.start()
        self.client.connect(self.address)
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.shutdown()
        self.server.shutdown()
        self.server_thread.terminate()


@pytest.fixture(scope='function')
def random_socket():
    return get_random_ipc_socket()


@pytest.fixture(scope='function')
def simple_server():
    server = Server()
    methods = server.methods

    @methods.register
    def method1(request):
        return u"Hello, world!"

    @methods.register
    def method2(request, name):
        return u"Hello, {0}!".format(name)

    @methods.register
    def method3(request, greeting=u'Hello', name=u'world'):
        if not isinstance(greeting, basestring):
            raise ValueError("Greeting must be a string")
        if not isinstance(name, basestring):
            raise ValueError("Name must be a string")
        return u"{0}, {1}!".format(greeting, name)

    @methods.register
    def get_list(request):
        return ['this', 'is', 'a', 'list']

    @methods.register
    def get_dict(request):
        return {'this': 'is', 'a': 'dict'}

    @methods.register
    def raise_value_error(request, *a, **kw):
        raise ValueError

    @methods.register
    def divide_by_zero(request):
        return 10 / 0

    route1 = server.routes['route1']

    @route1.register(name='method1')
    def r1m1(request):
        return "route1-method1"

    @route1.register(name='method2')
    def r1m2(request):
        return "route1-method2"

    @route1.register(name='method3')
    def r1m3(request):
        return "route1-method3"

    route2 = server.routes['route2']

    @route2.register(name='method1')
    def r2m1(request):
        return "route2-method1"

    @route2.register(name='method2')
    def r2m2(request):
        return "route2-method2"

    @route2.register(name='method3')
    def r2m3(request):
        return "route2-method3"

    route3 = server.routes['route3']

    @route3.register(name='method1')
    def r3m1(request):
        return "route3-method1"

    return server


@pytest.fixture(scope='function')
def multiroute_server():
    server = Server()

    route1 = server.routes['route1']
    route2 = server.routes['route2']
    route3 = server.routes['route3']

    @route1.register(name='method1')
    def r1m1(request):
        return "route1-method1"

    @route1.register(name='method2')
    def r1m2(request):
        return "route1-method2"

    @route1.register(name='method3')
    def r1m3(request):
        return "route1-method3"

    @route2.register(name='method1')
    def r2m1(request):
        return "route2-method1"

    @route2.register(name='method2')
    def r2m2(request):
        return "route2-method2"

    @route2.register(name='method3')
    def r2m3(request):
        return "route2-method3"

    @route3.register(name='method1')
    def r3m1(request):
        return "route3-method1"

    return server


@pytest.fixture(scope='function')
def simple_server_thread(request, random_socket, simple_server):
    th = ServerProcessThread(simple_server, random_socket)
    th.address = random_socket
    th.start()

    def cleanup():
        th.terminate()

    request.addfinalizer(cleanup)
    return th


@pytest.fixture(scope='function')
def simple_server_client(request, simple_server_thread):
    client = Client(simple_server_thread.address)

    def cleanup():
        client.shutdown()
        simple_server_thread.terminate()
    request.addfinalizer(cleanup)

    return client


@pytest.fixture(scope='function')
def simple_server_socket(request, simple_server_thread):
    ctx = zmq.Context()
    socket = ctx.socket(zmq.REQ)
    socket.connect(simple_server_thread.address)

    def cleanup():
        socket.close()
        ctx.term()
        ctx.destroy()
    request.addfinalizer(cleanup)

    return socket


@pytest.fixture(scope='function')
def multiroute_server_client(random_socket, multiroute_server):
    client = Client()
    return ServerClientPair(multiroute_server, client, random_socket)
