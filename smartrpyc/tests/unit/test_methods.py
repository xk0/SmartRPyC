import unittest

from smartrpyc.server import MethodsRegister


class SmartRPCTest(unittest.TestCase):

    def test_registration(self):
        register = MethodsRegister()

        func = lambda x: x
        register.register(func)
        register.register(name="test-x")(func)
        register.register(func, name="test-y")
        self.assertEqual(register.lookup("<lambda>"), func)
        self.assertEqual(register.lookup("test-x"), func)
        self.assertEqual(register.lookup("test-y"), func)

    def test_no_callable(self):
        register = MethodsRegister()
        with self.assertRaises(ValueError):
            register.register("not_callable")
            register.register("not_callable", "test")
