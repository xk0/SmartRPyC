# from smartrpyc.tests.utils import unittest

import pytest
from smartrpyc.server import MethodsRegister


class TestMethodsRegister(object):

    def test_registration(self):
        register = MethodsRegister()

        func = lambda x: x
        register.register(func)
        register.register(name="test-x")(func)
        register.register(func, name="test-y")
        assert register.lookup("<lambda>") == func
        assert register.lookup("test-x") == func
        assert register.lookup("test-y") == func

    def test_no_callable(self):
        register = MethodsRegister()
        with pytest.raises(ValueError):
            register.register("not_callable")
            register.register("not_callable", "test")
