# coding=utf-8
"""
Tests for SmartRPyC introspection
"""

from smartrpyc.client import IntrospectableClient
from smartrpyc.server import MethodsRegister, IntrospectionMiddleware
from smartrpyc.tests import utils
from smartrpyc.utils import get_random_ipc_socket


class TestIntrospection(object):

    def get_methods(self):
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
        return methods

    def test_list_methods(self):
        addr = get_random_ipc_socket()
        with utils.TestingServer(
                self.get_methods(), addr,
                middleware=[IntrospectionMiddleware()]):
            client = IntrospectableClient(addr)
            exposed_methods = dir(client)
            for meth in ('method1', 'method2', 'method3'):
                assert meth in exposed_methods

            assert client.method1.__doc__ == \
                'Returns the string "Hello, world!".'
            assert client.method2.__doc__ == 'Docstring of method2()'
            assert client.method3.__doc__ == 'Docstring of method3()'
