from typing import Optional

import logging
import ssl
import certifi
import os
import asyncio
import websockets
from pyneuphonic.lib import parse_proxies


class NeuphonicSocketManager:
    def __init__(
        self,
        NEUPHONIC_API_TOKEN,
        WEBSOCKET_URL,
        on_audio=None,
        on_non_audio=None,
        on_open=None,
        on_close=None,
        on_error=None,
        on_ping=None,
        on_pong=None,
        logger=None,
        timeout=None,
        proxies: Optional[dict] = None,
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

        self.on_audio = on_audio
        self.on_non_audio = on_non_audio
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
            self.WEBSOCKET_URL,
            ssl=ssl_context,
            timeout=self.timeout,
            **self._proxy_params,
        )

        self.logger.debug(
            f'WebSocket connection has been established: {self.WEBSOCKET_URL}, proxies: {self._proxy_params}',
        )

        self._callback(self.on_open)

    async def send_message(self, message):
        self.logger.debug(f'Sending message to Neuphonic WebSocket Server: {message}')
        await self.ws.send(message)

    async def ping(self):
        try:
            await self.ws.ping()
            self.logger.debug('Ping sent to WebSocket server.')
        except Exception as e:
            self.logger.error(f'Error sending ping: {e}')
            self._handle_exception(e)

    async def ping_periodically(self, interval: int = 20):
        while True:
            await self.ping()
            await asyncio.sleep(interval)

    async def _handle_message(self):
        try:
            async for message in self.ws:
                if isinstance(message, bytes):
                    self._callback(self.on_audio, message)  # handle audio messages
                else:
                    self._callback(self.on_non_audio, message)  # handle everything else
        except websockets.exceptions.ConnectionClosedError as e:
            self.logger.error(f'WebSocket connection closed: {e}')
            self._handle_exception(e)
        except Exception as e:
            self.logger.error(f'Exception in message_handler: {e}')
            self._handle_exception(e)
        finally:
            self._callback(self.on_close)

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
                self._handle_exception(e)
            except Exception as e:
                self.logger.error(f'Error in WebSocket process: {e}')
                self._handle_exception(e)
            finally:
                if self.ws.open:
                    await self.ws.close()
                await asyncio.sleep(5)  # wait before attempting to reconnect

    async def close(self):
        if self.ws and self.ws.open:
            await self.ws.close()
            self.logger.debug('Websocket connection closed.')

    def _callback(self, callback, *args):
        if callback:
            try:
                callback(self, *args)
            except Exception as e:
                self.logger.error(f'Error from callback {callback}: {e}')
                self._handle_exception(e)

    def _handle_exception(self, e):
        if self.on_error:
            self.on_error(self, e)
        else:
            raise e
