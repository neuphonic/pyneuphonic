import logging
from typing import Optional, Callable, Awaitable, Any
from types import MethodType

from pyneuphonic.websocket import NeuphonicSocketManager


class NeuphonicWebsocketClient(NeuphonicSocketManager):
    def __init__(
        self,
        NEUPHONIC_API_TOKEN: str = None,
        NEUPHONIC_WEBSOCKET_URL: str = None,
        logger: Optional[logging.Logger] = None,
        timeout: Optional[float] = None,
        proxies: Optional[dict] = None,
        on_audio_message: Optional[
            Callable[[type(NeuphonicSocketManager), bytes], Awaitable[None]]
        ] = None,
        on_non_audio_message: Optional[
            Callable[[type(NeuphonicSocketManager), Any], Awaitable[None]]
        ] = None,
        on_open: Optional[
            Callable[[type(NeuphonicSocketManager)], Awaitable[None]]
        ] = None,
        on_close: Optional[
            Callable[[type(NeuphonicSocketManager)], Awaitable[None]]
        ] = None,
        on_error: Optional[
            Callable[[type(NeuphonicSocketManager), Exception], Awaitable[None]]
        ] = None,
        on_ping: Optional[
            Callable[[type(NeuphonicSocketManager)], Awaitable[None]]
        ] = None,
        on_pong: Optional[
            Callable[[type(NeuphonicSocketManager)], Awaitable[None]]
        ] = None,
    ):
        super().__init__(
            NEUPHONIC_API_TOKEN,
            NEUPHONIC_WEBSOCKET_URL,
            logger=logger,
            timeout=timeout,
            proxies=proxies,
        )

        # bind the passed in methods to the class instance, if they were passed in, so that the NeuphonicSocketManager
        # plays the right methods at the right time
        if on_open:
            self.on_open = MethodType(on_open, self)

        if on_audio_message:
            self.on_audio_message = MethodType(on_audio_message, self)

        if on_non_audio_message:
            self.on_non_audio_message = MethodType(on_non_audio_message, self)

        if on_close:
            self.on_close = MethodType(on_close, self)

        if on_error:
            self.on_error = MethodType(on_error, self)

        if on_ping:
            self.on_ping = MethodType(on_ping, self)

        if on_pong:
            self.on_pong = MethodType(on_pong, self)
