# from smartrpyc.tests.utils import unittest

import pytest
from smartrpyc.server import MethodsRegister


def test_methods_register_no_regression():
    register = MethodsRegister()

    ## Try registering stuff with the old interface
    func = lambda x: x
    register.register(func=func)
    register.register(name="test-x")(func)
    register.register(func, name="test-y")
    assert register.lookup("<lambda>") == func
    assert register.lookup("test-x") == func
    assert register.lookup("test-y") == func

    ## Try registering non-callables..
    with pytest.raises(TypeError):  # sorry, but this actually is a TypeError!
        register.register("not_callable")
        register.register("not_callable", "test")


def test_methods_register():
    register = MethodsRegister()
    route1 = MethodsRegister()
    route2 = MethodsRegister()
    route1_1 = MethodsRegister()

    register.route(name='route1', obj=route1)
    register.route(name='route2', obj=route2)
    route1.route(name='sub1', obj=route1_1)

    @register.method(name='m1')
    def root_m1():
        return "ROOT-M1"

    @register.method
    def root_m2():
        return "ROOT-M2"

    @route1.method(name='m1')
    def route1_m1():
        return "R1-M1"

    @route1.method
    def route1_m2():
        return "R1-M2"

    @route2.method(name='m1')
    def route2_m1():
        return "R2-M1"

    @route2.method
    def route2_m2():
        return "R2-M2"

    @route1_1.method(name='m1')
    def route1_1_m1():
        return "R1-1-M1"

    @route1_1.method
    def route1_1_m2():
        return "R1-1-M2"

    @register.route
    class route3(MethodsRegister):
        def __init__(self, *a, **kw):
            # super(route3, self).__init__(*a, **kw)
            MethodsRegister.__init__(self, *a, **kw)
            self._methods = {
                'one': lambda: 'spam',
                'two': lambda: 'eggs',
                'three': lambda: 'bacon'}

    @register.route(name='route4')
    class ThisIsRoute4(MethodsRegister):
        pass

    assert register.get_route('') == register
    assert register.get_route('route1') == route1
    assert register.get_route('route1.sub1') == route1_1
    assert register.get_route('route2') == route2
    assert isinstance(register.get_route('route3'), route3)
    assert isinstance(register.get_route('route4'), ThisIsRoute4)

    assert sorted(register.list_routes()) == \
        ['route1', 'route2', 'route3', 'route4']
    assert sorted(register.list_routes('route1')) == ['sub1']
    assert sorted(register.list_routes('route1.sub1')) == []
    assert sorted(register.list_routes('route2')) == []

    assert sorted(register.list_methods()) == ['m1', 'root_m2']
    assert sorted(register.list_methods('route1')) == ['m1', 'route1_m2']
    assert sorted(register.list_methods('route1.sub1')) == \
        ['m1', 'route1_1_m2']
    assert sorted(register.list_methods('route2')) == ['m1', 'route2_m2']

    assert register.get_method('', 'm1') == root_m1
    assert register.get_method('', 'root_m2') == root_m2
    assert register.get_method('route1', 'm1') == route1_m1
    assert register.get_method('route1', 'route1_m2') == route1_m2
    assert register.get_method('route1.sub1', 'm1') == route1_1_m1
    assert register.get_method('route1.sub1', 'route1_1_m2') == route1_1_m2
    assert register.get_method('route2', 'm1') == route2_m1
    assert register.get_method('route2', 'route2_m2') == route2_m2

    assert register.get_method('route3', 'one')() == 'spam'


def test_methods_register_validation():
    register = MethodsRegister()
    with pytest.raises(TypeError):
        register.route(name=123, obj={})
    with pytest.raises(TypeError):
        register.method(name='invalid', func=123.45)
    with pytest.raises(TypeError):
        register.method(name='invalid', func='hello')
    with pytest.raises(TypeError):
        register.method(name=123, func=lambda x: x)
