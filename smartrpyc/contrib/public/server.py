"""
"Public API" server

.. note::
    This is just a stub, taken from another project that contains
    a fully-featured implementation of the thing.. Feel free to copy
    in your project or subclass this.
"""

from smartrpyc.utils import lazy_property
from smartrpyc.exceptions import LoginRequired, NotAuthorized
from smartrpyc.server import Request, Server, ServerMiddlewareBase


class PublicRequest(Request):
    """
    Request class from the Public RPC (supports authentication)
    """

    @lazy_property
    def token(self):
        return self.raw.get('t')

    @lazy_property
    def token_info(self):
        ## todo: return information about the authorization token
        ##       such as permissions and expiration date
        pass

    @property
    def user_id(self):
        return self.token_info['user_id']

    @lazy_property
    def user(self):
        if self.token is None:
            return None
        ## todo: return information on the user linked to the token

    def is_logged_in(self):
        return self.user is not None

    def check_permissions(self, permissions):
        ## todo: Make sure the token id valid and grants the selected perms
        pass


class AuthCheckMiddleware(ServerMiddlewareBase):
    def pre(self, request, method):
        if hasattr(method, 'login_required') and method.login_required:
            if not request.is_logged_in():
                raise LoginRequired("You must be logged in.")
        if hasattr(method, 'require_permissions'):
            try:
                request.check_permissions(method.require_permissions)
            except:
                raise NotAuthorized("You miss some required permission(s)")


class PublicServer(Server):
    request_class = PublicRequest

    def __init__(self, *a, **kw):
        super(PublicServer, self).__init__(*a, **kw)
        self.middleware.append(AuthCheckMiddleware())


def login_required(fun):
    """
    Decorator for RPC methods -- requires login
    """
    fun.login_required = True
    return fun


def require_permissions(*permissions):
    """
    Decorator for RPC methods -- requires permissions
    """
    def decorator(fun):
        fun.require_permissions = permissions
        return fun
    return decorator
