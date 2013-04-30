"""
Exceptions used by the Server.
"""

__all__ = ['DirectResponse', 'SetMethod']


class DirectResponse(Exception):
    """
    Exception used by middleware to directly send a response to the client.

    Request processing will be terminated immediately and the response
    sent to the client, as a normal response.
    """
    def __init__(self, response):
        self.response = response


class SetMethod(Exception):
    """
    Exception used by middleware to change the method to be executed.

    As a side effect, this clears all the previous "method not found"
    exceptions.
    """
    def __init__(self, method):
        self.method = method
