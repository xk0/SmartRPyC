smartrpyc.server.middleware
###########################

.. py:currentmodule:: smartrpyc.server.middleware


.. note::
    The middleware handling part needs some rethinking.

    * How do we decide whether to interrupt the request upon
      exception raising inside middleware?

    * Do we want to execute the post middleware in any case, or just
      in case the request was processed in a clean way?

      * I think POST middleware should have a chance to know that an
        exception was raised and do something about it.

    * When should we use middleware and when would it be better to
      subclass Server instead?



Middleware base
===============

Middleware can be used to extend the server functionality, by adding
methods to be executed before and after the request is processed.

.. autoclass:: ServerMiddlewareBase
    :members:
    :undoc-members:


Introspection Middleware
========================

.. autoclass:: IntrospectionMiddleware
    :members:
    :undoc-members:
