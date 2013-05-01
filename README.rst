##########
SmartRPyC
##########

A small but powerful RPC library for Python, powered by ZeroMQ_.

:Version: 0.1-beta5
:Build status:
    .. image:: https://travis-ci.org/xk0/SmartRPyC.png
        :alt: Build status
        :target: https://travis-ci.org/xk0/SmartRPyC
:Authors:
    * Samuele Santi
    * Flavio Percoco
:Links:
    * `SmartRPyC GitHub pages`_
    * `SmartRPyC source code`_
    * `SmartRPyC documentation`_
    * `SmartRPyC CheeseShop`_

.. _ZeroMQ: http://www.zeromq.org/
.. _SmartRPyC documentation: http://pythonhosted.org/SmartRPyC/
.. _SmartRPyC GitHub pages: http://xk0.github.io/SmartRPyC/
.. _SmartRPyC source code: https://github.com/xk0/SmartRPyC
.. _SmartRPyC CheeseShop: https://pypi.python.org/pypi/SmartRPyC

Installing
==========

To install it, just::

    pip install smartrpyc

or, if you want the latest version from git::

    pip install git+git://github.com/xk0/SmartRPyC.git


Compatibility
=============

The library has been test and is known to work on:

* CPython 2.6
* CPython 2.7
* CPython 3.2
* CPython 3.3

**Note:** Python3 support is provided via 2to3 conversion, automatically
handled by distribute on install. Everything should work just fine.

**Note:** There currently are some problems with PyPy due to dependency
on C extensions.


Usage
=====

Have a look at the `SmartRPyC documentation`_.


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


Testing
=======

From the sources folder::

    python setup.py test


