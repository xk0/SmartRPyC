# coding=utf-8
"""
Tests for SmartRPC
"""

import random

import zmq
import msgpack

from smartrpyc.client import Client, RemoteException
from smartrpyc.server import MethodsRegister
from smartrpyc.utils import get_random_ipc_socket
from smartrpyc.tests import utils


# noinspection PyUnusedLocal
class SmartRPCTest(utils.FunctionalTest):
    def setUp(self):

        methods = MethodsRegister()

        @methods.register
        def method1(request):
            return u"Hello, world!"

        @methods.register
        def method2(request, name):
            return u"Hello, {}!".format(name)

        @methods.register
        def method3(request, greeting=u'Hello', name=u'world'):
            if not isinstance(greeting, basestring):
                raise ValueError("Greeting must be a string")
            if not isinstance(name, basestring):
                raise ValueError("Name must be a string")
            return u"{}, {}!".format(greeting, name)

        @methods.register
        def get_list(request):
            return ['this', 'is', 'a', 'list']

        @methods.register
        def get_dict(request):
            return {'this': 'is', 'a': 'dict'}

        @methods.register
        def raise_value_error(request, *a, **kw):
            raise ValueError

        self.addr = get_random_ipc_socket()
        self.start_server(methods, self.addr)

    def tearDown(self):
        self.stop_server()

    def test_simple_call(self):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect(self.addr)
        socket.send(msgpack.packb({
            'm': 'method1',
        }, encoding='utf-8'))
        response = msgpack.unpackb(socket.recv(), encoding='utf-8')
        self.assertDictEqual({'r': 'Hello, world!'}, response)

    def test_concurrent_calls(self):
        context = zmq.Context()
        sockets = {}
        socket_ids = range(10)

        random.shuffle(socket_ids)
        for i in socket_ids:
            sockets[i] = context.socket(zmq.REQ)
            sockets[i].connect(self.addr)

        random.shuffle(socket_ids)
        for i in socket_ids:
            sockets[i].send(msgpack.packb({
                'm': 'method2',
                'a': ['socket {}'.format(i)],
            }, encoding='utf-8'))

        random.shuffle(socket_ids)
        for i in socket_ids:
            response = msgpack.unpackb(sockets[i].recv(), encoding='utf-8')
            self.assertDictEqual(
                {'r': 'Hello, socket {}!'.format(i)},
                response)

    def test_call_with_args(self):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect(self.addr)
        socket.send(msgpack.packb({
            'm': 'method2',
            'a': ['WORLD'],
        }, encoding='utf-8'))
        response = msgpack.unpackb(socket.recv(), encoding='utf-8')
        self.assertDictEqual({'r': 'Hello, WORLD!'}, response)

    def test_call_with_args_utf8(self):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect(self.addr)

        socket.send(msgpack.packb({
            'm': 'method2',
            'a': [u'WORLD'],
        }, encoding='utf-8'))
        response = msgpack.unpackb(socket.recv(), encoding='utf-8')
        self.assertDictEqual({'r': u'Hello, WORLD!'}, response)

        socket.send(msgpack.packb({
            'm': 'method2',
            'a': [u'Ẅøřłđ'],
        }, encoding='utf-8'))
        response = msgpack.unpackb(socket.recv(), encoding='utf-8')
        self.assertDictEqual(
            {'r': u'Hello, Ẅøřłđ!'},
            response)

    def test_call_with_kwargs(self):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect(self.addr)
        socket.send(msgpack.packb({
            'm': 'method2',
            'k': {'name': 'WORLD'},
        }, encoding='utf-8'))
        response = msgpack.unpackb(socket.recv(), encoding='utf-8')
        self.assertDictEqual({'r': 'Hello, WORLD!'}, response)

    def test_call_with_multi_args(self):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect(self.addr)

        socket.send(msgpack.packb({
            'm': 'method3',
            'k': {'name': 'WORLD'},
        }, encoding='utf-8'))
        response = msgpack.unpackb(socket.recv(), encoding='utf-8')
        self.assertDictEqual({'r': 'Hello, WORLD!'}, response)

        socket.send(msgpack.packb({
            'm': 'method3',
            'k': {'greeting': 'HOWDY'},
        }, encoding='utf-8'))
        response = msgpack.unpackb(socket.recv(), encoding='utf-8')
        self.assertDictEqual({'r': 'HOWDY, world!'}, response)

        socket.send(msgpack.packb({
            'm': 'method3',
            'k': {'greeting': 'HOWDY', 'name': 'MAN'},
        }, encoding='utf-8'))
        response = msgpack.unpackb(socket.recv(), encoding='utf-8')
        self.assertDictEqual({'r': 'HOWDY, MAN!'}, response)

        socket.send(msgpack.packb({
            'm': 'method3',
            'a': ('hey', 'man'),
        }, encoding='utf-8'))
        response = msgpack.unpackb(socket.recv(), encoding='utf-8')
        self.assertDictEqual({'r': 'hey, man!'}, response)

    def test_with_client(self):
        client = Client(self.addr)
        self.assertEqual('Hello, world!', client.method1())

        with self.assertRaises(RemoteException):
            client.method1('this', 'does not', 'accept arguments!')

        self.assertEqual(u'Hello, WORLD!', client.method2(u'WORLD'))
        self.assertEqual(u'Hello, WORLD!', client.method2(name=u'WORLD'))
        self.assertEqual(u'Hello, Ẅøřłđ!', client.method2(name=u'Ẅøřłđ'))

        self.assertEqual('Hi, man!', client.method3('Hi', 'man'))
        self.assertEqual('Hi, man!', client.method3(greeting='Hi', name='man'))
        self.assertEqual('Hi, world!', client.method3(greeting='Hi'))

        with self.assertRaises(RemoteException):
            client.method3('HELLO', greeting='Hi')

        self.assertListEqual(client.get_list(), ['this', 'is', 'a', 'list'])
        self.assertDictEqual(client.get_dict(), {'this': 'is', 'a': 'dict'})

        with self.assertRaises(RemoteException):
            client.raise_value_error()

        ## Ok, the method doesn't exist, no big deal..
        with self.assertRaises(RemoteException):
            client.no_such_method()

        client.method1()  # The server must still be alive here..
