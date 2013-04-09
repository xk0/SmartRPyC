# coding=utf-8
"""
Tests for SmartRPC
"""

import random
import unittest
from multiprocessing import Process, Lock

import zmq
import msgpack

from smartrpyc import MethodsRegister, Server, Client, RemoteException
from smartrpyc.utils import get_random_ipc_socket


class ExampleRpcProcess(Process):
    daemon = True

    def __init__(self, methods, addresses=None, middleware=None):
        super(ExampleRpcProcess, self).__init__()
        self._methods = methods
        self._addresses = addresses
        self._middleware = middleware

    def run(self):
        self.rpc = Server(self._methods, self._addresses)
        if self._middleware is not None:
            self.rpc.middleware[:] = self._middleware[:]
        self.rpc.run()


# noinspection PyUnusedLocal
class SmartRPCTest(unittest.TestCase):
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
        self.rpc_process = ExampleRpcProcess(methods, self.addr)
        self.rpc_process.start()

    def tearDown(self):
        self.rpc_process.terminate()

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


# class SmartrpcMiddlewareTest(unittest.TestCase):
#     def setUp(self):
#         self.addr = addresses = get_random_ipc_socket()
#         lock = Lock()
#
#         def run_rpc_daemon():
#             methods = MethodsRegister()
#
#             @methods.register
#             def method1(request):
#                 return u"Hello, world!"
#
#             @methods.register
#             def method2(request):
#                 return u"Hello, world! #2"
#             method2.login_required = True
#
#             @methods.register
#             def raise_value_error(request, *a, **kw):
#                 raise ValueError
#
#             class DummyLoginMiddleware(object):
#                 # noinspection PyUnusedLocal
#                 def pre(self, request, method):
#                     auth = request.raw.get('auth')
#                     if auth != ['user', 'password']:
#                         raise ValueError("Login failed")
#
#             class UppercaseMiddleware(object):
#                 # noinspection PyUnusedLocal
#                 def post(self, request, method, response, exception):
#                     return response.upper()
#
#             addresses = self.addr
#             middleware = [DummyLoginMiddleware(), UppercaseMiddleware()]
#
#             rpc = Server(methods, addresses)
#             if middleware is not None:
#                 rpc.middleware[:] = middleware[:]
#
#             lock.release()
#             rpc.run()
#
#         self.proc = Process(target=run_rpc_daemon)
#         self.proc.daemon = True
#         lock.acquire()
#         self.proc.start()
#         lock.acquire()
#
#     def tearDown(self):
#         self.proc.terminate()
#
#     def test_without_login(self):
#         client = Client(self.addr)
#
#         with self.assertRaises(RemoteException):
#             client.method1()
#
#         with self.assertRaises(RemoteException):
#             client.method2()
#
#     def test_with_login(self):
#         class ClientLoginMiddleware(object):
#             def __init__(self, username, password):
#                 self.username, self.password = username, password
#
#             def pre(self, request):
#                 request['auth'] = (self.username, self.password)
#                 return request
#
#         client = Client(self.addr)
#         client.middleware.append(ClientLoginMiddleware('user', 'password'))
#
#         self.assertEqual(u'HELLO, WORLD!', client.method1())
#         self.assertEqual(u'HELLO, WORLD! #2', client.method2())
