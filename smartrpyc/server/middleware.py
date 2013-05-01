"""
Server middleware
"""
import logging
from smartrpyc.server import DirectResponse

__all__ = ['ServerMiddlewareBase', 'IntrospectionMiddleware']

logger = logging.getLogger(__name__)


class ServerMiddlewareBase(object):
    """
    Base class for the server middleware.

    This is mostly a reminder for methods signatures, but subclassing
    from this object is not mandatory for middleware classes, as long
    as they expose a ``pre()`` and/or ``post()`` methods.
    """

    def pre(self, request, method):
        """
        This method will be executed **before** the request is processed.

        :param request:
            a :py:class:`smartrpyc.server.Request` object
        :param method:
            the method that is going to be called to process the request
            and generate the response

        This method has different ways to hijack the request/response
        process:

        * Raise a :py:exc:`~smartrpyc.server.DirectResponse` exception,
          containing some object to be directly returned to the client

        * Raise a :py:exc:`~smartrpyc.server.SetMethod` exception,
          containing an alternate method to be called

        * Raise a generic exception that will terminate the request
          processing and will be returned to the client directly.
        """
        pass

    def post(self, request, method, response, exception):
        """
        This method will be executed **after** the request is processed
        and a response returned by the called method.

        :param request:
            a :py:class:`smartrpyc.server.Request` object
        :param method:
            the method that has been called to process the request
            and generate the response
        :param response:
            the response object returned from the method call (if any)
        :param exception:
            the exception raised by the method call (if any)
        """
        pass


class IntrospectionMiddleware(object):
    """
    Middleware adding the ``.dir()`` and ``.doc()`` methods to be used
    for introspecting the exposed methods.
    """

    def pre(self, request, method):
        ## Note: this is experimental, method names may change!
        if request.method == 'dir':
            logger.debug('Called .dir() method')
            raise DirectResponse(request.server.methods.list_methods())
        if request.method == 'doc':
            logger.debug('Called .doc() method for method {0}'
                         ''.format(request.args[0]))
            _method = request.server.methods.lookup(request.args[0])
            raise DirectResponse(_method.__doc__)
