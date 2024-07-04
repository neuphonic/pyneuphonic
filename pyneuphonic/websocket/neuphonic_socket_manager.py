import logging
import ssl
import certifi
import os
import asyncio
import websockets
from pyneuphonic.websocket.libs import parse_proxies
from typing import Optional


class NeuphonicSocketManager:
    def __init__(
        self,
        NEUPHONIC_API_TOKEN: str = None,
        NEUPHONIC_WEBSOCKET_URL: str = None,
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

        if NEUPHONIC_WEBSOCKET_URL is None:
            NEUPHONIC_WEBSOCKET_URL = os.getenv('NEUPHONIC_WEBSOCKET_URL')

            if NEUPHONIC_WEBSOCKET_URL is None:
                raise EnvironmentError(
                    'NEUPHONIC_WEBSOCKET_URL has not been passed in and is not set in the environment.'
                )

        if not logger:
            logger = logging.getLogger(__name__)

        self.logger = logger

        self._NEUPHONIC_API_TOKEN = NEUPHONIC_API_TOKEN
        self.NEUPHONIC_WEBSOCKET_URL = NEUPHONIC_WEBSOCKET_URL
        self.timeout = timeout

        self.ws = None

        self._proxy_params = parse_proxies(proxies) if proxies else {}

    async def create_ws_connection(self):
        self.logger.debug(
            f'Creating connection with WebSocket Server: {self.NEUPHONIC_WEBSOCKET_URL}, proxies: {self._proxy_params}',
        )

        ssl_context = ssl.create_default_context(cafile=certifi.where())

        self.ws = await websockets.connect(
            f'{self.NEUPHONIC_WEBSOCKET_URL}/{self._NEUPHONIC_API_TOKEN}',
            ssl=ssl_context,
            timeout=self.timeout,
            **self._proxy_params,
        )

        self.logger.debug(
            f'WebSocket connection has been established: {self.NEUPHONIC_WEBSOCKET_URL}, proxies: {self._proxy_params}',
        )

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
            await self.on_error(e)

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
                    await self.on_audio_message(message)
                else:
                    self.logger.debug(f'Handling non-audio message: {message}')
                    await self.on_non_audio_message(message)
        except websockets.exceptions.ConnectionClosedError as e:
            self.logger.error(f'WebSocket connection closed: {e}')
            await self.on_error(e)
        except Exception as e:
            self.logger.error(f'Exception in message_handler: {e}')
            await self.on_error(e)
        finally:
            self.logger.error('On close')
            await self.on_close()

    async def open(self):
        await self.create_ws_connection()
        await self.on_open()

    async def listen(self):
        while True:
            try:
                receive_task = asyncio.create_task(self._handle_message())
                ping_task = asyncio.create_task(self.ping_periodically())

                await asyncio.wait(
                    [receive_task, ping_task], return_when=asyncio.FIRST_COMPLETED
                )

            except websockets.exceptions.ConnectionClosedError as e:
                self.logger.error('Lost websocket connection')
                await self.on_error(e)
            except Exception as e:
                self.logger.error(f'Error in WebSocket process: {e}')
                await self.on_error(e)
            finally:
                if self.ws.open:
                    await self.ws.close()
                await asyncio.sleep(5)  # wait before attempting to reconnect

    async def close(self):
        if self.ws and self.ws.open:
            await self.ws.close()
            self.logger.debug('Websocket connection closed.')

    async def on_audio_message(self, message: bytes):
        pass

    async def on_non_audio_message(self, message: bytes):
        pass

    async def on_open(self):
        pass

    async def on_close(self):
        pass

    async def on_error(self, e: Exception):
        raise e

    async def on_ping(self):
        pass

    async def on_pong(self):
        pass
