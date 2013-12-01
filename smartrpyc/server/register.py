"""
Method Registers module

This module provides facilities for preparing a library of methods
to be exposed via the RPC.

The library creation can happen in several ways:

* Using a :py:class:`.MethodsRegister` decorator, to register a bunch
  of stand-alone functions
* Usinng a :py:class:`.MethodsObject` to expose all the methods in a
  given object (instance). This is especially useful if you need
  to expose methods from an object **instance**, ie. you need to share
  some state.
"""

import warnings


__all__ = ['BaseMethodsRegister', 'SimpleMethodsRegister',
           'MethodsRegister', 'MethodsObject']


class BaseMethodsRegister(object):
    def get_route(self, route):
        raise NotImplementedError

    def get_method(self, route, method):
        raise NotImplementedError

    def list_routes(self, base=None):
        raise NotImplementedError

    def list_methods(self, route=None):
        raise NotImplementedError

    def lookup(self, name):
        warnings.warn("The lookup() method is deprecated. "
                      "Use get_method() instead.", DeprecationWarning)
        return self.get_method(None, name)


class SimpleMethodsRegister(BaseMethodsRegister):
    def __init__(self, routes=None, methods=None):
        self._routes = routes or {}
        self._methods = methods or {}

    def get_route(self, route):
        parts = filter(None, route.split('.', 1))
        if len(parts) == 0:
            return self
        route = self._routes[parts[0]]
        if len(parts > 1):
            return route.get_route(parts[1])
        return route

    def get_method(self, route, method):
        if route is None:
            return self._methods[method]
        return self.get_route(route).get_method(None, method)

    def list_routes(self, base=None):
        if base is None:
            return self._routes.iterkeys()
        return self.get_route(base).list_routes()

    def list_methods(self, base=None):
        if base is None:
            return self._methods.iterkeys()
        return self.get_route(base).list_methods()


class MethodsRegister(SimpleMethodsRegister):
    """
    Register for methods to be exposed via RPC.
    Mostly a wrapper around a dict.

    Usage::

        methods = MethodsRegister()

        @methods.register
        def my_method(request, arg1, arg2):
            pass

        @methods.register(name='method2')
        def my_other_method(request, arg1=123, arg2=None):
            pass

        methods.register(func=func, name='test')

        # then pass methods to the Server() constructor
    """

    def register(self, func=None, name=None):
        """
        Refer to class docstring

        :params func: Callable to register
        :params name: Basestring to use as reference
            name for `func`
        """

        # If name is None we'll get the name from the
        # function itself.
        name = name or callable(func) and func.__name__

        def decorator(func):
            self._register(name, func)
            return func

        # If func is not None, it means the method
        # has been used either as a simple decorator
        # or as a plain method. The function will be
        # registered by calling decorator, otherwise,
        # decorator will be returned.
        if func is None:
            return decorator
        return decorator(func)

    def _register(self, name, function):
        """
        Method used to finally register a
        function.

        :params name:
            Functions lookup name
        :params function:
            Callable function
        """
        if (name is not None) and not isinstance(name, basestring):
            raise ValueError("Invalid name: must be a string")
        if not callable(function):
            raise ValueError("Invalid function: must be a callable")

        if name is None:
            name = function.__name__

        self._methods[name] = function

    def route(self, obj=None, name=None):
        """
        Register a new route
        """
        def decorator(obj):
            self._route(name, obj)
            return obj
        if obj is None:
            return decorator
        return decorator(obj)

    def _route(self, name, obj):
        self._routes[name] = obj


class MethodsObject(BaseMethodsRegister):
    """
    Objects wrapper register.

    This is a "wrapper" register, that automatically exposes all the methods
    contained in the object passed to the constructor.
    """

    _object = None

    def lookup(self, method):
        return getattr(self._object, method)

    def list_methods(self):
        return [m for m in dir(self._object) if not m.startswith('_')]

    def set_object(self, obj):
        if self._object is not None:
            raise RuntimeError("You cannot set the object twice.")
        self._object = obj
