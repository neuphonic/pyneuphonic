import json
import logging
import ssl
import certifi
import os
import asyncio
import websockets

from pyneuphonic.websocket.libs import parse_proxies
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

        This client is initialised with the provided callbacks. These provided callbacks will be bound to the instance
        of this client class, and as per the type signatures, each of these callbacks should take an instance of this
        class as the first argument. The callbacks are free to create as many attributes on the client instance as they
        desire (see the pyaudio and sounddevice examples in pyneuphonic.websocket.common).

        Alternatively, this class can be inherited by a child class with the callback functions being overridden. Both
        methods achieve the same goal.
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
        self._initialise_callbacks(
            on_message,
            on_open,
            on_close,
            on_error,
            on_ping,
            on_pong,
            on_send,
        )

    def _initialise_callbacks(
        self,
        on_message,
        on_open,
        on_close,
        on_error,
        on_ping,
        on_pong,
        on_send,
    ):
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

        self._logger.debug('Completed initialising callbacks.')

    async def create_ws_connection(self, ping_interval, ping_timeout):
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
        Open the websocket connection.

        Parameters
        ----------
        ping_interval : int
            The number of seconds to wait between every PING.
        ping_timeout : int
            The number of seconds to wait for a PONG from the websocket server before assuming a timeout error.
        """
        await self.create_ws_connection(ping_interval, ping_timeout)
        await self.on_open()

    async def listen(self):
        """
        Start listening to the server and handling responses.

        The client must have been opened using NeuphonicWebsocketClient.open. Incoming messages will be forwarded to
        NeuphonicWebsocketClient.on_message after being converted into a dict object.
        """

        async def _listen(client):
            while client._ws.open:
                try:
                    receive_task = asyncio.create_task(client._handle_message())

                    await asyncio.wait(
                        [receive_task], return_when=asyncio.FIRST_COMPLETED
                    )

                except websockets.exceptions.ConnectionClosedError as e:
                    client._logger.error('Lost websocket connection')
                    await client.on_error(e)
                except Exception as e:
                    client._logger.error(f'Error in WebSocket process: {e}')
                    await client.on_error(e)
                finally:
                    if client._ws.open:
                        await client._ws.close()

        self._listen_task = asyncio.create_task(_listen(self))

    async def close(self, force: bool = False):
        """
        Close the websocket connection and call the NeuphonicWebsocketClient.on_close function.

        Parameters
        ----------
        force : bool
            Default is False and function will wait for all audio to be received by the websocket (for any text that has
            already been sent). If this is set to True, then the websocket will close the connection and you may miss
            any audio snippets not yet receieved.

        Returns
        -------

        """

        async def cancel_listen_task():
            try:
                self._listen_task.cancel()
                await self._listen_task
            except asyncio.CancelledError as e:
                pass

        def check_all_audio_received():
            if self._last_sent_message is None:
                return True
            elif self._last_received_message and self._last_sent_message:
                received_text = self._last_received_message['data']['text']
                chars_to_check = min(len(self._last_sent_message), len(received_text))

                if (
                    received_text[-chars_to_check:]
                    == self._last_sent_message[-chars_to_check:]
                ):
                    return True

            return False

        if self._listen_task:
            while not check_all_audio_received() and not force:
                await asyncio.sleep(0.1)

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
