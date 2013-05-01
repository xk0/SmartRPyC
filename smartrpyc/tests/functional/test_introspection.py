# coding=utf-8
"""
Tests for SmartRPyC introspection
"""

from smartrpyc.client import IntrospectableClient
from smartrpyc.server import MethodsRegister, IntrospectionMiddleware
from smartrpyc.tests import utils
from smartrpyc.utils import get_random_ipc_socket

# import cool_logging
# cool_logging.getLogger('smartrpyc.server')


class TestIntrospection(utils.FunctionalTest):

    def start_server(self, methods, addresses):
        self.rpc_process = utils.ExampleRpcProcess(
            methods,
            addresses,
            middleware=[IntrospectionMiddleware()])
        self.rpc_process.start()
        return self.rpc_process

    def setUp(self):
        methods = MethodsRegister()

        def method1(request):
            """Returns the string "Hello, world!"."""
            return u"Hello, world!"

        def method2(request, name):
            """Docstring of method2()"""
            return u"Hello, {0}!".format(name)

        def method3(request, greeting=u'Hello', name=u'world'):
            """Docstring of method3()"""
            if not isinstance(greeting, basestring):
                raise ValueError("Greeting must be a string")
            if not isinstance(name, basestring):
                raise ValueError("Name must be a string")
            return u"{0}, {1}!".format(greeting, name)

        methods.register(method1)
        methods.register(method2)
        methods.register(method3)

        self.addr = get_random_ipc_socket()
        self.start_server(methods, self.addr)

    def tearDown(self):
        self.stop_server()

    def test_list_methods(self):
        client = IntrospectableClient(self.addr)
        exposed_methods = dir(client)
        for meth in ('method1', 'method2', 'method3'):
            self.assertIn(meth, exposed_methods)

        self.assertEqual(client.method1.__doc__,
                         'Returns the string "Hello, world!".')
        self.assertEqual(client.method2.__doc__, 'Docstring of method2()')
        self.assertEqual(client.method3.__doc__, 'Docstring of method3()')
