"""
"Public API" client
"""

from smartrpyc.client import Client


class PublicClient(Client):
    """
    Client for the public API.
    Includes what needed to handle authentication tokens.
    """

    def __init__(self, *a, **kw):
        super(PublicClient, self).__init__(*a, **kw)
        self._token = None

    def _prepare_request(self, request):
        if self._token is not None:
            request['t'] = self._token
        return request

    def login(self, username, password):
        """Performs a login, storing token to be used in further requests"""
        self._token = self.authenticate(username, password)

    def set_token(self, token):
        """Directly set the token to be used for authentication"""
        self._token = token

    def logout(self):
        """Logs out, removing authorization token"""
        self._token = None
