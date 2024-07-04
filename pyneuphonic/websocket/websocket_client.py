import logging
from typing import Optional, Callable, Awaitable, Any

from pyneuphonic.websocket import NeuphonicSocketManager


class NeuphonicWebsocketClient(NeuphonicSocketManager):
    def __init__(
        self,
        NEUPHONIC_API_TOKEN: str,
        WEBSOCKET_URL: str,
        on_audio_message: Optional[
            Callable[['NeuphonicSocketManager', bytes], Awaitable[None]]
        ] = None,
        on_non_audio_message: Optional[
            Callable[['NeuphonicSocketManager', Any], Awaitable[None]]
        ] = None,
        on_open: Optional[Callable[['NeuphonicSocketManager'], Awaitable[None]]] = None,
        on_close: Optional[
            Callable[['NeuphonicSocketManager'], Awaitable[None]]
        ] = None,
        on_error: Optional[
            Callable[['NeuphonicSocketManager', Exception], Awaitable[None]]
        ] = None,
        on_ping: Optional[Callable[['NeuphonicSocketManager'], Awaitable[None]]] = None,
        on_pong: Optional[Callable[['NeuphonicSocketManager'], Awaitable[None]]] = None,
        logger: Optional[logging.Logger] = None,
        timeout: Optional[float] = None,
        proxies: Optional[dict] = None,
    ):
        super().__init__(
            NEUPHONIC_API_TOKEN,
            WEBSOCKET_URL,
            on_audio_message=on_audio_message,
            on_non_audio_message=on_non_audio_message,
            on_open=on_open,
            on_close=on_close,
            on_error=on_error,
            on_ping=on_ping,
            on_pong=on_pong,
            logger=logger,
            timeout=timeout,
            proxies=proxies,
        )

        self.audio_buffer = bytearray()
