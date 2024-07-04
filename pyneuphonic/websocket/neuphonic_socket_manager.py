import logging
import ssl
import certifi
import os
import asyncio
import websockets
from pyneuphonic.lib import parse_proxies
from typing import Callable, Optional, Any, Awaitable


class NeuphonicSocketManager:
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
        timeout: Optional[float] = None,  # TODO
        proxies: Optional[dict] = None,  # TODO - implement SSL with this
    ):
        if NEUPHONIC_API_TOKEN is None:
            NEUPHONIC_API_TOKEN = os.getenv('NEUPHONIC_API_TOKEN')

            if NEUPHONIC_API_TOKEN is None:
                raise EnvironmentError(
                    'NEUPHONIC_API_TOKEN has not been passed in and is not set in the environment.'
                )

        if not logger:
            logger = logging.getLogger(__name__)

        self.logger = logger

        self._NEUPHONIC_API_TOKEN = NEUPHONIC_API_TOKEN
        self.WEBSOCKET_URL = WEBSOCKET_URL

        self.on_audio_message = on_audio_message
        self.on_non_audio_message = on_non_audio_message
        self.on_open = on_open
        self.on_close = on_close
        self.on_error = on_error
        self.timeout = timeout
        self.on_ping = on_ping
        self.on_pong = on_pong

        self.ws = None

        self._proxy_params = parse_proxies(proxies) if proxies else {}

    async def create_ws_connection(self):
        self.logger.debug(
            f'Creating connection with WebSocket Server: {self.WEBSOCKET_URL}, proxies: {self._proxy_params}',
        )

        ssl_context = ssl.create_default_context(cafile=certifi.where())

        self.ws = await websockets.connect(
            f'{self.WEBSOCKET_URL}/{self._NEUPHONIC_API_TOKEN}',
            ssl=ssl_context,
            timeout=self.timeout,
            **self._proxy_params,
        )

        self.logger.debug(
            f'WebSocket connection has been established: {self.WEBSOCKET_URL}, proxies: {self._proxy_params}',
        )

        await self._callback(self.on_open)

    async def send_message(self, message):
        self.logger.debug(f'Sending message to Neuphonic WebSocket Server: {message}')

        if self.ws:
            await self.ws.send(message)
        else:
            self.logger.debug('Failed to send message, no WebSocket Server available')

    async def ping(self):
        try:
            await self.ws.ping()
            self.logger.debug('Ping sent to WebSocket server.')
        except Exception as e:
            self.logger.error(f'Error sending ping: {e}')
            await self._handle_exception(e)

    async def ping_periodically(self, interval: int = 20):
        while True:
            await self.ping()
            await asyncio.sleep(interval)

    async def _handle_message(self):
        try:
            async for message in self.ws:
                self.logger.debug('Received message.')
                if isinstance(message, bytes):
                    self.logger.debug(f'Handling audio message: {len(message)} bytes')
                    await self._callback(
                        self.on_audio_message, message
                    )  # handle audio messages
                else:
                    self.logger.debug(f'Handling non-audio message: {message}')
                    await self._callback(
                        self.on_non_audio_message, message
                    )  # handle everything else
        except websockets.exceptions.ConnectionClosedError as e:
            self.logger.error(f'WebSocket connection closed: {e}')
            await self._handle_exception(e)
        except Exception as e:
            self.logger.error(f'Exception in message_handler: {e}')
            await self._handle_exception(e)
        finally:
            self.logger.error('On close')
            await self._callback(self.on_close)

    async def start(self):
        while True:
            try:
                await self.create_ws_connection()

                receive_task = asyncio.create_task(self._handle_message())
                ping_task = asyncio.create_task(self.ping_periodically())

                await asyncio.wait(
                    [receive_task, ping_task], return_when=asyncio.FIRST_COMPLETED
                )

            except websockets.exceptions.ConnectionClosedError as e:
                self.logger.error('Lost websocket connection')
                await self._handle_exception(e)
            except Exception as e:
                self.logger.error(f'Error in WebSocket process: {e}')
                await self._handle_exception(e)
            finally:
                if self.ws.open:
                    await self.ws.close()
                await asyncio.sleep(5)  # wait before attempting to reconnect

    async def close(self):
        if self.ws and self.ws.open:
            await self.ws.close()
            self.logger.debug('Websocket connection closed.')

    async def _callback(self, callback, *args):
        self.logger.debug(f'Callback {callback} called with {type(args), len(args)}')
        if callback:
            try:
                await callback(self, *args)
            except Exception as e:
                self.logger.error(f'Error from callback {callback}: {e}')
                await self._handle_exception(e)

    async def _handle_exception(self, e):
        if self.on_error:
            self.on_error(self, e)
        else:
            raise e
