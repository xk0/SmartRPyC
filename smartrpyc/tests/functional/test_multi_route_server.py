"""
Test for SmartRPyC server with multiple routes
"""


import random

import zmq
import msgpack
import pytest

from smartrpyc.client import Client, RemoteException
from smartrpyc.server import MethodsRegister, Server
from smartrpyc.utils import get_random_ipc_socket
from smartrpyc.tests import utils


#@pytest.fixture
def ipc_socket():
    return get_random_ipc_socket()


#@pytest.fixture
def server_obj():
    server = Server()

    route1 = server.routes['route1']
    route2 = server.routes['route2']
    route3 = server.routes['route3']

    #server.routes[''] = server.routes['route1']  # Just a test..

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


def test_smartrpyc_multi_route():
    addr = ipc_socket()
    srv = server_obj()

    for k, route in srv.routes.iteritems():
        assert isinstance(route, MethodsRegister)
        assert hasattr(route, 'lookup')

    server_proc = utils.NewTestingServer(srv, addresses=addr)
    with server_proc:
        client = Client(addr)
        assert client['route1'].method1() == 'route1-method1'
        assert client['route1'].method2() == 'route1-method2'
        assert client['route1'].method3() == 'route1-method3'
        assert client['route2'].method1() == 'route2-method1'
        assert client['route2'].method2() == 'route2-method2'
        assert client['route2'].method3() == 'route2-method3'
        assert client['route3'].method1() == 'route3-method1'
