"""
Server middleware
"""
import logging
from smartrpyc.server import DirectResponse

__all__ = ['ServerMiddlewareBase', 'IntrospectionMiddleware']

logger = logging.getLogger(__name__)


class ServerMiddlewareBase(object):
    """
    Base class for server middleware.
    (mostly a reminder for methods signatures, subclassing from
    this is not mandatory).
    """

    def pre(self, request, method):
        pass

    def post(self, request, method, response, exception):
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
            logger.debug('Called .doc() method for method {}'
                         ''.format(request.args[0]))
            _method = request.server.methods.lookup(request.args[0])
            raise DirectResponse(_method.__doc__)
