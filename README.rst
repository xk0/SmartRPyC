SmartRPyC
#########

A smart RPC library for Python, powered by ZeroMQ.

:author: Samuele Santi
:version: 0.1-beta
:url: https://github.com/rshk/SmartRPyC


.. image:: https://travis-ci.org/rshk/SmartRPyC.png
    :alt: Build status
    :target: https://travis-ci.org/rshk/SmartRPyC


Installing
==========

To install it, just::

    pip install smartrpyc

or::

    pip install git+git://github.com/rshk/SmartRPyC.git


Testing
=======

From the sources folder::

    python setup.py test


Usage
=====

...more coming soon, for now, have a look a the tests :)


Why not ZeroRPC?
================

While `dotCloud's ZeroRPC`_ is a very valid project, there are some
things I wanted to improve over it:

* **More Pythonic:** I didn't need to support cross-language compatibility,
  so I opted for improving the support for Python, by allowing things
  like keyword arguments.

* **Simpler:** I didn't need some features offered by ZeroRPC

* **Some bugfixes:** for example, we're not sharing the same ZeroRPC
  context for everything, as this would cause issues when running
  in a multithreaded environment (eg. when using the client in a flask view).

.. _dotCloud's ZeroRPC: http://zerorpc.dotcloud.com/
