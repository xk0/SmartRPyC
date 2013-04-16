SmartRPyC
#########

A smart RPC library for Python, powered by ZeroMQ.

.. image:: https://travis-ci.org/xk0/SmartRPyC.png
    :alt: Build status
    :target: https://travis-ci.org/xk0/SmartRPyC

:Author: Samuele Santi
:Version: 0.1-beta
:URL: https://github.com/xk0/SmartRPyC


Installing
==========

To install it, just::

    pip install smartrpyc

or::

    pip install git+git://github.com/xk0/SmartRPyC.git


Testing
=======

From the sources folder::

    python setup.py test


Usage
=====

More documentation coming soon, for now, have a look a the tests :)


Why not ZeroRPC?
================

While `dotCloud's ZeroRPC`_ is a very valid project, there are some
things I wanted to improve over it:

* **More Pythonic:** I didn't need to support cross-language compatibility,
  so I opted for improving the support for Python, by allowing things
  like keyword arguments.

* **Simpler:** I didn't need some features offered by ZeroRPC,
  while I needed the ability to extend the library to add some other.

* **Support middleware:** for things like authentication management,
  it's way better to have the server/client handle what needed in
  the background, than doing ugly things such as adding a "token"
  argument to every call requiring authentication.

* **Some bugfixes:** for example, we're not sharing the same ZeroRPC
  context for everything, as this would cause issues when running
  in a multithreaded environment (eg. when using the client in a flask view).

.. _dotCloud's ZeroRPC: http://zerorpc.dotcloud.com/
