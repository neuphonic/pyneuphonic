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
        setup_audio_player: Optional[
            Callable[['NeuphonicWebsocketClient'], Awaitable[None]]
        ] = None,
        teardown_audio_player: Optional[
            Callable[['NeuphonicWebsocketClient'], Awaitable[None]]
        ] = None,
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

        self.setup_audio_player = setup_audio_player
        self.teardown_audio_player = teardown_audio_player

    async def start(self):
        if self.setup_audio_player:
            await self.setup_audio_player(self)
            self.logger.debug('Audio player setup completed.')

        self.logger.debug('NeuphonicWebsocketClient.start')
        await super().start()

    async def stop(self):
        await super().close()

        if self.teardown_audio_player:
            await self.teardown_audio_player(self)
