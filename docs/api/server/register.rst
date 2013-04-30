smartrpyc.server.register
#########################

.. py:currentmodule:: smartrpyc.server.register


This module provides facilities for preparing a library of methods
to be exposed via the RPC.

The library creation can happen in several ways:

* Using a :py:class:`.MethodsRegister` decorator, to register a bunch
  of stand-alone functions
* Usinng a :py:class:`.MethodsObject` to expose all the methods in a
  given object (instance). This is especially useful if you need
  to expose methods from an object **instance**, ie. you need to share
  some state.


Base for the Method Register objects
====================================

This class provides an abstract of the methods that can (and should)
be exposed by a methods register object.

.. autoclass:: MethodsRegisterBase
    :members:
    :undoc-members:


Methods register
================

.. autoclass:: MethodsRegister
    :members:
    :undoc-members:


Methods object
==============

.. note:: I don't like the name and I think I'll change it soon.

.. autoclass:: MethodsObject
    :members:
    :undoc-members:
