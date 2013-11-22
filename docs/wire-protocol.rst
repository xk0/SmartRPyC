The wire protocol
#################

How does the actual communication between clients and servers work?

* Transmitted messages are dictionaries, encoded using a different
  choice of serializers (currently supported are: msgpack (default),
  json, pickle)

* Everything is passed around via ZeroMQ sockets

.. note:: All key names are single-letter to save up space..


Structure of a request message
==============================

The main keys are:

* ``i`` -- A request identifier, used eg. for deduplication purposes
* ``r`` -- The route of the object which method is to be called
* ``m`` -- The method to be called
* ``a`` -- Arguments for the call
* ``k`` -- Keyword arguments for the call


Structure of a response message
===============================

Response messages are dicts with a single key, named ``r``,
containing the return value. This is needed to distinguish
from exceptions.


Structure of an exception message
=================================

Keys of an exception message are:

* ``e`` -- Name of the exception that was raised
* ``e_msg`` -- string representation of the exception

