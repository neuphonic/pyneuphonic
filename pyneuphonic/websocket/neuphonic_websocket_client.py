import json
import logging
import ssl
import certifi
import os
import asyncio
import websockets
import importlib.util

from pyneuphonic.websocket.libs import parse_proxies
from pyneuphonic.websocket.common.pyaudio import (
    on_open as on_open_pyaudio,
    on_message as on_message_pyaudio,
    on_close as on_close_pyaudio,
)
from typing import Optional, Callable, Awaitable
from types import MethodType


class NeuphonicWebsocketClient:
    def __init__(
        self,
        NEUPHONIC_API_TOKEN: str = None,
        NEUPHONIC_WEBSOCKET_URL: str = None,
        on_message: Optional[
            Callable[['NeuphonicWebsocketClient', dict], Awaitable[None]]
        ] = None,
        on_open: Optional[
            Callable[['NeuphonicWebsocketClient'], Awaitable[None]]
        ] = None,
        on_close: Optional[
            Callable[['NeuphonicWebsocketClient'], Awaitable[None]]
        ] = None,
        on_error: Optional[
            Callable[['NeuphonicWebsocketClient', Exception], Awaitable[None]]
        ] = None,
        on_ping: Optional[
            Callable[['NeuphonicWebsocketClient'], Awaitable[None]]
        ] = None,
        on_pong: Optional[
            Callable[['NeuphonicWebsocketClient'], Awaitable[None]]
        ] = None,
        on_send: Optional[
            Callable[['NeuphonicWebsocketClient', str], Awaitable[None]]
        ] = None,
        logger: Optional[logging.Logger] = None,
        timeout: Optional[float] = None,  # TODO
        proxies: Optional[dict] = None,  # TODO
    ):
        """
        Websocket client for the Neuphonic TTS Engine.

        This client is initialised with the provided callbacks.
        If no callbacks are provided and PyAudio is installed, the client will automatically detect PyAudio and use it
        to play audio.
        The callbacks should all take the instance of this class as the first argument, and the type signatures should
        be as per the provided type hints.
        The callbacks are called when the corresponding event occurs.

        Parameters
        ----------
        NEUPHONIC_API_TOKEN
            The API token for the Neuphonic TTS Engine.
        NEUPHONIC_WEBSOCKET_URL
            The URL for the Neuphonic TTS Engine websocket.
        on_message
            The callback function to be called when a message is received from the websocket server.
        on_open
            The callback function to be called when the websocket connection is opened.
        on_close
            The callback function to be called when the websocket connection is closed.
        on_error
            The callback function to be called when an error occurs.
        on_ping
            The callback function to be called when a PING is received from the websocket server. Not yet implemented.
        on_pong
            The callback function to be called when a PONG is received from the websocket server. Not yet implemented.
        on_send
            The callback function to be called when a message is sent to the websocket server.
        logger
            The logger to be used by the client. If not provided, a logger will be created.
        timeout
            The timeout for the websocket connection.
        proxies
            The proxies to be used by the websocket connection.
        """
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

        self._logger = logger

        self._NEUPHONIC_API_TOKEN = NEUPHONIC_API_TOKEN
        self._NEUPHONIC_WEBSOCKET_URL = NEUPHONIC_WEBSOCKET_URL
        self._timeout = timeout

        self._ws = None
        self._listen_task = None
        self._last_sent_message = None
        self._last_received_message = None

        self._proxy_params = parse_proxies(proxies) if proxies else {}
        self._bind_callbacks(
            on_message,
            on_open,
            on_close,
            on_error,
            on_ping,
            on_pong,
            on_send,
        )

    def _bind_callbacks(
        self,
        on_message,
        on_open,
        on_close,
        on_error,
        on_ping,
        on_pong,
        on_send,
    ):
        """
        Initialises the callbacks for the websocket client. Binds callbacks to the class instance.
        """
        self._logger.debug('Initialising callbacks.')

        if on_message:
            self.on_message = MethodType(on_message, self)

        if on_open:
            self.on_open = MethodType(on_open, self)

        if on_close:
            self.on_close = MethodType(on_close, self)

        if on_error:
            self.on_error = MethodType(on_error, self)

        if on_ping:
            self.on_ping = MethodType(on_ping, self)

        if on_pong:
            self.on_pong = MethodType(on_pong, self)

        if on_send:
            self.on_send = MethodType(on_send, self)

        if importlib.util.find_spec('pyaudio') is not None and (
            on_message is None and on_open is None and on_close is None
        ):
            self._logger.debug('Using PyAudio to play audio.')
            # if pyaudio is installed, and no callbacks are provided, use the pyaudio callbacks to play audio
            self.on_open = MethodType(on_open_pyaudio, self)
            self.on_close = MethodType(on_close_pyaudio, self)
            self.on_message = MethodType(on_message_pyaudio, self)

        self._logger.debug('Callbacks initialised.')

    async def _create_ws_connection(self, ping_interval, ping_timeout):
        """
        Creates the websocket connection and saves it into self._ws

        This function is called by the open function and should not be called directly.

        Parameters
        ----------
        ping_interval : int
            The number of seconds to wait between every PING.
        ping_timeout : int
            The number of seconds to wait for a PONG from the websocket server before assuming a timeout error.
        """
        self._logger.debug(
            f'Creating connection with WebSocket Server: {self._NEUPHONIC_WEBSOCKET_URL}, proxies: {self._proxy_params}',
        )

        if 'wss' in self._NEUPHONIC_WEBSOCKET_URL[:3]:
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            self._logger.debug('Creating Encrypted SLL Connection.')
        else:
            ssl_context = None
            self._logger.debug('Creating Unencrypted Connection.')

        self._ws = await websockets.connect(
            f'{self._NEUPHONIC_WEBSOCKET_URL}/{self._NEUPHONIC_API_TOKEN}',
            ssl=ssl_context,
            timeout=self._timeout,
            ping_interval=ping_interval,
            ping_timeout=ping_timeout,
            **self._proxy_params,
        )

        self._logger.debug(
            f'WebSocket connection has been established: {self._NEUPHONIC_WEBSOCKET_URL}, proxies: {self._proxy_params}',
        )

    async def send(self, message: str):
        """
        Send a string to the Neuphonic websocket.

        Parameters
        ----------
        message : str
            The string to send to the websocket.
        """
        if self._ws and message:
            self._logger.debug(
                f'Sending message to Neuphonic WebSocket Server: {message}'
            )
            self._last_sent_message = message
            await self._ws.send(message)
            await self.on_send(message)
        else:
            self._logger.debug('Failed to send message, no WebSocket Server available')

    async def ping(self):
        try:
            await self._ws.ping()
            self._logger.debug('Ping sent to WebSocket server.')
        except Exception as e:
            self._logger.error(f'Error sending ping: {e}')
            await self.on_error(e)

    async def _handle_message(self):
        """
        Handle incoming messages from the websocket server.

        This function is called by the listen function and should not be called directly.
        """
        try:
            async for message in self._ws:
                message = json.loads(message)
                self._last_received_message = message
                await self.on_message(message)
        except websockets.exceptions.ConnectionClosedError as e:
            self._logger.error(f'WebSocket connection closed: {e}')
            await self.on_error(e)
        except Exception as e:
            self._logger.error(f'Exception in message_handler: {e}')
            await self.on_error(e)
        finally:
            self._logger.debug('_handle_message.finally block')
            await self.on_close()

    async def open(self, ping_interval: int = 20, ping_timeout: int = None):
        """
        Open the websocket connection and start listening to incoming messages.

        Parameters
        ----------
        ping_interval : int
            The number of seconds to wait between every PING.
        ping_timeout : int
            The number of seconds to wait for a PONG from the websocket server before assuming a timeout error.
        """
        await self._create_ws_connection(ping_interval, ping_timeout)
        await self.on_open()
        await self._listen()

    async def _listen(self):
        """
        Start listening to the server and handling responses.

        This function is called by the open function and should not be called directly.
        """

        async def _listen_task(client):
            if client._ws.open:  # if the client is open
                try:
                    receive_task = asyncio.create_task(client._handle_message())
                    await receive_task
                except websockets.exceptions.ConnectionClosedError as e:
                    client._logger.error('Lost websocket connection')
                    await client.on_error(e)
                except Exception as e:
                    client._logger.error(f'Error in WebSocket process: {e}')
                    await client.on_error(e)
                finally:
                    if client._ws.open:
                        await client._ws.close()

        self._listen_task = asyncio.create_task(_listen_task(self))

    async def close(self):
        """
        Close the websocket connection and call the NeuphonicWebsocketClient.on_close function.
        """

        async def cancel_listen_task():
            """Stop listening to the websocket responses"""
            try:
                self._listen_task.cancel()
                await self._listen_task
            except asyncio.CancelledError as e:
                pass

        if self._listen_task:
            await cancel_listen_task()

        if self._ws and self._ws.open:
            await self._ws.close()
            await self.on_close()

        self._logger.debug('Websocket connection closed.')

    async def on_message(self, message: dict):
        """
        This function is called on every incoming message. It receives the message as a python dict object.

        Parameters
        ----------
        message : dict
            The incoming message from the websocket server.
        """
        pass

    async def on_open(self):
        """Called after the websocket connection opens."""
        pass

    async def on_close(self):
        """Called after the websocket connection closes."""
        pass

    async def on_error(self, e: Exception):
        """
        Called on error.

        Parameters
        ----------
        e : Exception
            The error raised.
        """
        raise e

    async def on_ping(self, *args, **kwargs):
        pass

    async def on_pong(self, *args, **kwargs):
        pass

    async def on_send(self, message: str):
        """
        Called every time a message is sent to the server.

        Parameters
        ----------
        message : str
            The message sent to the server.
        """
        pass
