"""
Exceptions returned to the client from the RPC API.
"""


class RpcServiceException(Exception):
    pass


class LoginFailed(RpcServiceException):
    pass


class LoginRequired(RpcServiceException):
    pass


class NotAuthorized(RpcServiceException):
    pass
