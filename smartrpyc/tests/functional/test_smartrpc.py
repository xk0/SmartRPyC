# coding=utf-8
"""
Tests for SmartRPC
"""

import random

import zmq
import msgpack
import pytest

from smartrpyc.client import Client, RemoteException
from smartrpyc.server import MethodsRegister
from smartrpyc.utils import get_random_ipc_socket
from smartrpyc.tests import utils


# noinspection PyUnusedLocal
class TestSmartrpcFunctionality(object):
    def get_methods(self):

        methods = MethodsRegister()

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

        return methods

    def test_simple_call(self):
        addr = get_random_ipc_socket()
        with utils.TestingServer(methods=self.get_methods(), addresses=addr):
            context = zmq.Context()
            socket = context.socket(zmq.REQ)
            socket.connect(addr)
            socket.send(msgpack.packb({
                'm': 'method1',
            }, encoding='utf-8'))
            response = msgpack.unpackb(socket.recv(), encoding='utf-8')
            assert response == {'r': 'Hello, world!'}

    def test_concurrent_calls(self):
        addr = get_random_ipc_socket()
        with utils.TestingServer(methods=self.get_methods(), addresses=addr):

            context = zmq.Context()
            sockets = {}
            socket_ids = range(10)

            random.shuffle(socket_ids)
            for i in socket_ids:
                sockets[i] = context.socket(zmq.REQ)
                sockets[i].connect(addr)

            random.shuffle(socket_ids)
            for i in socket_ids:
                sockets[i].send(msgpack.packb({
                    'm': 'method2',
                    'a': ['socket {0}'.format(i)],
                }, encoding='utf-8'))

            random.shuffle(socket_ids)
            for i in socket_ids:
                response = msgpack.unpackb(sockets[i].recv(), encoding='utf-8')
                assert response == {'r': 'Hello, socket {0}!'.format(i)}

    def test_call_with_args(self):
        addr = get_random_ipc_socket()
        with utils.TestingServer(methods=self.get_methods(), addresses=addr):
            context = zmq.Context()
            socket = context.socket(zmq.REQ)
            socket.connect(addr)
            socket.send(msgpack.packb({
                'm': 'method2',
                'a': ['WORLD'],
            }, encoding='utf-8'))
            response = msgpack.unpackb(socket.recv(), encoding='utf-8')
            assert response == {'r': 'Hello, WORLD!'}

    def test_call_with_args_utf8(self):
        addr = get_random_ipc_socket()
        with utils.TestingServer(methods=self.get_methods(), addresses=addr):

            context = zmq.Context()
            socket = context.socket(zmq.REQ)
            socket.connect(addr)

            socket.send(msgpack.packb({
                'm': 'method2',
                'a': [u'WORLD'],
            }, encoding='utf-8'))
            response = msgpack.unpackb(socket.recv(), encoding='utf-8')
            assert response == {'r': u'Hello, WORLD!'}

            socket.send(msgpack.packb({
                'm': 'method2',
                'a': [u'Ẅøřłđ'],
            }, encoding='utf-8'))
            response = msgpack.unpackb(socket.recv(), encoding='utf-8')
            assert response == {'r': u'Hello, Ẅøřłđ!'}

    def test_call_with_kwargs(self):
        addr = get_random_ipc_socket()
        with utils.TestingServer(methods=self.get_methods(), addresses=addr):
            context = zmq.Context()
            socket = context.socket(zmq.REQ)
            socket.connect(addr)
            socket.send(msgpack.packb({
                'm': 'method2',
                'k': {'name': 'WORLD'},
            }, encoding='utf-8'))
            response = msgpack.unpackb(socket.recv(), encoding='utf-8')
            assert response == {'r': 'Hello, WORLD!'}

    def test_call_with_multi_args(self):
        addr = get_random_ipc_socket()
        with utils.TestingServer(methods=self.get_methods(), addresses=addr):
            context = zmq.Context()
            socket = context.socket(zmq.REQ)
            socket.connect(addr)

            socket.send(msgpack.packb({
                'm': 'method3',
                'k': {'name': 'WORLD'},
            }, encoding='utf-8'))
            response = msgpack.unpackb(socket.recv(), encoding='utf-8')
            assert response == {'r': 'Hello, WORLD!'}

            socket.send(msgpack.packb({
                'm': 'method3',
                'k': {'greeting': 'HOWDY'},
            }, encoding='utf-8'))
            response = msgpack.unpackb(socket.recv(), encoding='utf-8')
            assert response == {'r': 'HOWDY, world!'}

            socket.send(msgpack.packb({
                'm': 'method3',
                'k': {'greeting': 'HOWDY', 'name': 'MAN'},
            }, encoding='utf-8'))
            response = msgpack.unpackb(socket.recv(), encoding='utf-8')
            assert response == {'r': 'HOWDY, MAN!'}

            socket.send(msgpack.packb({
                'm': 'method3',
                'a': ('hey', 'man'),
            }, encoding='utf-8'))
            response = msgpack.unpackb(socket.recv(), encoding='utf-8')
            assert response == {'r': 'hey, man!'}

    def test_with_client(self):
        addr = get_random_ipc_socket()
        with utils.TestingServer(methods=self.get_methods(), addresses=addr):
            client = Client(addr)
            assert client.method1() == 'Hello, world!'

            with pytest.raises(RemoteException):
                client.method1('this', 'does not', 'accept arguments!')

            assert client.method2(u'WORLD') == u'Hello, WORLD!'
            assert client.method2(name=u'WORLD') == u'Hello, WORLD!'
            assert client.method2(name=u'Ẅøřłđ') == u'Hello, Ẅøřłđ!'

            assert client.method3('Hi', 'man') == 'Hi, man!'
            assert client.method3(greeting='Hi', name='man') == 'Hi, man!'
            assert client.method3(greeting='Hi') == 'Hi, world!'

            with pytest.raises(RemoteException):
                client.method3('HELLO', greeting='Hi')

            assert client.get_list() == ['this', 'is', 'a', 'list']
            assert client.get_dict() == {'this': 'is', 'a': 'dict'}

            with pytest.raises(RemoteException):
                client.raise_value_error()

            ## Ok, the method doesn't exist, no big deal..
            with pytest.raises(RemoteException):
                client.no_such_method()

            client.method1()  # The server must still be alive here..
