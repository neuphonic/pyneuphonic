import ssl
import certifi
import httpx
from typing import Optional


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

    def raise_for_status(self, response: httpx.Response, message: Optional[str] = None):
        if not response.is_success:
            raise httpx.HTTPStatusError(
                f"{message + ' ' if message is not None else ''}Status code: {response.status_code}. Error: {response.text}",
                request=response.request,
                response=response,
            )
