from typing import Optional
import os

from pyneuphonic._voices import Voices
from pyneuphonic._sse import SSEClient, AsyncSSEClient
from pyneuphonic._endpoint import Endpoint
from pyneuphonic._websocket import AsyncTTSWebsocketClient
from pyneuphonic._agents import Agents
from pyneuphonic._longform_inference import LongformInference


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
            it needs to be set in your environment and retrievable via `os.getenv('NEUPHONIC_API_KEY')`
        base_url : Optional[str], optional
            The base url pointing to which regional deployment to use. If this is not passed on
            and not set in `os.getenv('NEUPHONIC_API_URL')`, then it will default to
            'api.neuphonic.com'.
        """

        # Initialise the API key and base URL
        self._api_key = (
            api_key
            or os.getenv("NEUPHONIC_API_KEY")
            or os.getenv("NEUPHONIC_API_TOKEN")
        )
        if self._api_key is None:
            raise EnvironmentError(
                "`api_key` has not been passed in and `NEUPHONIC_API_KEY` is not set in the environment."
            )
        self._base_url = base_url or os.getenv("NEUPHONIC_API_URL", "api.neuphonic.com")

        self.voices = Voices(api_key=self._api_key, base_url=self._base_url)
        self.tts = TTS(api_key=self._api_key, base_url=self._base_url)
        self.agents = Agents(api_key=self._api_key, base_url=self._base_url)


class TTS(Endpoint):
    def SSEClient(self) -> SSEClient:
        return SSEClient(api_key=self._api_key, base_url=self._base_url)

    def AsyncSSEClient(self) -> AsyncSSEClient:
        return AsyncSSEClient(api_key=self._api_key, base_url=self._base_url)

    def AsyncWebsocketClient(self) -> AsyncTTSWebsocketClient:
        return AsyncTTSWebsocketClient(api_key=self._api_key, base_url=self._base_url)

    def LongformInference(self) -> LongformInference:
        return LongformInference(api_key=self._api_key, base_url=self._base_url)
