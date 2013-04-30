"""
Exceptions for the server
"""

__all__ = ['DirectResponse']


class DirectResponse(Exception):
    """
    Used by middleware classes to directly send a response to the client.
    Request processing will be terminated immediately and the response
    sent to the client, as a normal response.
    """
    def __init__(self, response):
        self.response = response


class SetMethod(Exception):
    """Change the method to be called"""
    def __init__(self, method):
        self.method = method
