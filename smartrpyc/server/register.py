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

__all__ = ['MethodsRegisterBase', 'MethodsRegister', 'MethodsObject']


class MethodsRegisterBase(object):
    """
    Base for the Method Register objects.

    This class provides an abstract of the methods that can (and should)
    be exposed by a methods register object.
    """

    def register(self, func=None, name=None):
        """Only used for registers supporting changes"""
        raise NotImplementedError

    def lookup(self, method):
        """
        The most important method, returning the appropriate
        method to be called.
        """
        raise NotImplementedError

    def list_methods(self):
        """List all the supported methods"""
        raise NotImplementedError


class MethodsRegister(MethodsRegisterBase):
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
    def __init__(self):
        self._methods = {}

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
            self.store(name, func)
            return func

        # If func is not None, it means the method
        # has been used either as a simple decorator
        # or as a plain method. The function will be
        # registered by calling decorator, otherwise,
        # decorator will be returned.
        return func and decorator(func) or decorator

    def store(self, name, function):
        """
        Method used to finally register a
        function.

        :params name:
            Functions lookup name
        :params function:
            Callable function
        """
        if not isinstance(name, basestring) and \
                not callable(function):
            # If we get here, most likely, the user has passed
            # a non callable function. See unittest for a clearer
            # example.
            raise ValueError("Unsupported arguments to register: "
                             "{0} and {1}".format(name, function))
        self._methods[name] = function

    def lookup(self, method):
        return self._methods[method]

    def list_methods(self):
        return self._methods.keys()


class MethodsObject(MethodsRegisterBase):
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
