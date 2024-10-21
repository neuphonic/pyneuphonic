import ssl
import certifi


class Endpoint:
    def __init__(
        self,
        api_key: str,
        base_url: str,
        timeout: int = 10,
    ):
        self._api_key = api_key
        self._base_url = base_url
        self.timeout = timeout

        self.headers = {
            'x-api-key': self._api_key,
        }

    @property
    def base_url(self):
        return self._base_url

    def _is_localhost(self):
        return True if 'localhost' in self.base_url else False

    @property
    def http_url(self):
        prefix = 'http' if self._is_localhost() else 'https'
        return f'{prefix}://{self.base_url}'

    @property
    def ws_url(self):
        prefix = 'ws' if self._is_localhost() else 'wss'
        return f'{prefix}://{self.base_url}'

    @property
    def ssl_context(self):
        ssl_context = (
            None
            if self._is_localhost()
            else ssl.create_default_context(cafile=certifi.where())
        )

        return ssl_context
