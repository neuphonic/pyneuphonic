from typing import Optional
import os

from pyneuphonic._voices import Voices
from pyneuphonic._sse import SSEClient, AsyncSSEClient
from pyneuphonic._endpoint import Endpoint
from pyneuphonic._websocket import AsyncWebsocketClient


class Neuphonic:
    """
    The client for Neuphonic's TTS (text-to-speech) python library.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """Constructor for the Neuphonic client.

        Parameters
        ----------
        api_key
            Your API key. Generate this on https://beta.neuphonic.com. If this is not passed in,
            it needs to be set in your environment and retrievable via `os.getenv('NEUPHONIC_API_TOKEN')`
        base_url : Optional[str], optional
            The base url pointing to which regional deployment to use. If this is not passed on
            and not set in `os.getenv('NEUPHONIC_API_URL')`, then it will default to
            'eu-west-1.api.neuphonic.com'.
        """
        if api_key is None:
            api_key = os.getenv('NEUPHONIC_API_TOKEN')

            if api_key is None:
                raise EnvironmentError(
                    '`api_key` has not been passed in and `NEUPHONIC_API_TOKEN` is not set in the environment.'
                )

        if base_url is None:
            base_url = os.getenv('NEUPHONIC_API_URL')

            if base_url is None:
                base_url = 'eu-west-1.api.neuphonic.com'

        self._api_key = api_key
        self._base_url = base_url

        self.voices = Voices(api_key=self._api_key, base_url=self._base_url)
        self.tts = TTS(api_key=self._api_key, base_url=self._base_url)


class TTS(Endpoint):
    def SSEClient(self, timeout: Optional[int] = 10) -> SSEClient:
        return SSEClient(
            api_key=self._api_key, base_url=self._base_url, timeout=timeout
        )

    def AsyncSSEClient(self, timeout: Optional[int] = 10) -> AsyncSSEClient:
        return AsyncSSEClient(
            api_key=self._api_key, base_url=self._base_url, timeout=timeout
        )

    def AsyncWebsocketClient(self) -> AsyncWebsocketClient:
        return AsyncWebsocketClient(api_key=self._api_key, base_url=self._base_url)
