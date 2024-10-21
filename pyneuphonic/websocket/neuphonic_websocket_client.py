import json
import logging
import ssl
import certifi
import os
import asyncio
import websockets
import importlib.util
import warnings

from pyneuphonic.websocket import (
    setup_pyaudio,
    play_audio,
    teardown_pyaudio,
)
from typing import Optional, Callable, Awaitable
from types import MethodType


class NeuphonicWebsocketClient:
    def __init__(
        self,
        NEUPHONIC_API_TOKEN: str = None,
        NEUPHONIC_API_URL: str = None,
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
        on_send: Optional[
            Callable[['NeuphonicWebsocketClient', str], Awaitable[None]]
        ] = None,
        language_id: str = 'en',
        play_audio: bool = True,
        sampling_rate: int = 22050,
        logger: Optional[logging.Logger] = None,
        timeout: Optional[float] = None,
        params: dict = None,
    ):
        """
        This websocket implementation has been DEPRECATED.

        Websocket client for the Neuphonic TTS Engine.

        This client is initialised with the provided callbacks.
        If `play_audio` is set to `True` and PyAudio is installed, the client will automatically detect PyAudio and use it
        to play audio.
        The callbacks should all take the instance of this class as the first argument, and the type signatures should
        be as per the provided type hints.
        The callbacks are called when the corresponding event occurs.

        Parameters
        ----------
        NEUPHONIC_API_TOKEN
            The API token for the Neuphonic TTS Engine. If this is not provided the it is loaded from the
            environment.
        NEUPHONIC_API_URL
            The URL for the Neuphonic TTS Engine websocket. This should be of the form `{aws-region}.api.neuphonic.com`
            Default is `eu-west-1.api.neuphonic.com`
        on_message
            The callback function to be called when a message is received from the websocket server.
        on_open
            The callback function to be called when the websocket connection is opened.
        on_close
            The callback function to be called when the websocket connection is closed.
        on_error
            The callback function to be called when an error occurs.
        on_send
            The callback function to be called when a message is sent to the websocket server.
        language_id
            The language id for the language to generate audio in. Currently only english ('en') is
            available. Default is 'en'.
        play_audio
            Whether to play audio from the websocket server automatically. This is true by default and will use pyaudio
            to play the audio. This will not affect any other callbacks passed in and will run alongside them.
        sampling_rate
            If play_audio is True, this is the sampling_rate to use for the default pyaudio player. Default
            is 22050 Hz.
        logger
            The logger to be used by the client. If not provided, a logger will be created.
        timeout
            The timeout for the websocket client.
        params
            Additional model parameters to be passed to the websocket connection. These will be added as
            query parameters to the websocket URL.
        """
        if NEUPHONIC_API_TOKEN is None:
            NEUPHONIC_API_TOKEN = os.getenv('NEUPHONIC_API_TOKEN')

            if NEUPHONIC_API_TOKEN is None:
                raise EnvironmentError(
                    'NEUPHONIC_API_TOKEN has not been passed in and is not set in the environment.'
                )

        if NEUPHONIC_API_URL is None:
            NEUPHONIC_API_URL = os.getenv('NEUPHONIC_API_URL')

            if NEUPHONIC_API_URL is None:
                NEUPHONIC_API_URL = 'eu-west-1.api.neuphonic.com'

        if not logger:
            logger = logging.getLogger(__name__)

        self._logger = logger

        self._NEUPHONIC_API_TOKEN = NEUPHONIC_API_TOKEN
        self._NEUPHONIC_API_URL = NEUPHONIC_API_URL
        self._timeout = timeout

        self._ws = None
        self._listen_task = None
        self._last_sent_message = None
        self._last_received_message = None
        self._language_id = language_id
        self._play_audio = play_audio
        self._sampling_rate = sampling_rate

        self._bind_callbacks(
            on_message,
            on_open,
            on_close,
            on_error,
            on_send,
        )

        self.params = params

    def _bind_callbacks(
        self,
        on_message,
        on_open,
        on_close,
        on_error,
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

        if on_send:
            self.on_send = MethodType(on_send, self)

        if importlib.util.find_spec('pyaudio') is not None and self._play_audio:
            self._logger.debug('Using PyAudio to play audio.')
            # if pyaudio is installed, and no callbacks are provided, use the pyaudio callbacks to play audio
            self.setup_pyaudio = MethodType(setup_pyaudio, self)
            self.teardown_pyaudio = MethodType(teardown_pyaudio, self)
            self.play_audio = MethodType(play_audio, self)
        elif importlib.util.find_spec('pyaudio') is None and self._play_audio:
            warnings.warn(
                'Parameter `play_audio` is True but PyAudio is not installed. No audio will be played.',
                UserWarning,
            )
            self._play_audio = False
        else:
            self._play_audio = False

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
            f'Creating connection with WebSocket Server: {self._NEUPHONIC_API_URL}, params: {self.params}',
        )

        # Construct the URL with query parameters
        protocol = 'wss' if 'localhost' not in self._NEUPHONIC_API_URL else 'ws'
        url = f'{protocol}://{self._NEUPHONIC_API_URL}/speak/{self._language_id}'
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        self._logger.debug('Creating Encrypted SLL Connection.')

        if self.params:
            query_string = '&'.join([f'{k}={v}' for k, v in self.params.items()])
            url += f'?{query_string}'

        self._ws = await websockets.connect(
            url,
            ssl=ssl_context if protocol == 'wss' else None,
            timeout=self._timeout,
            ping_interval=ping_interval,
            ping_timeout=ping_timeout,
            extra_headers={'x-api-key': self._NEUPHONIC_API_TOKEN},
        )

        self._logger.debug(
            f'WebSocket connection has been established: {self._NEUPHONIC_API_URL}',
        )

    async def send(self, message: str, autocomplete=False):
        """
        Send a string to the Neuphonic websocket.

        Parameters
        ----------
        message : str
            The string to send to the websocket.
        autocomplete : bool
            Whether or not to autocomplete the message.
        """
        if self._ws and message:
            self._logger.debug(
                f'Sending message to Neuphonic WebSocket Server: {message}'
            )
            self._last_sent_message = message

            if isinstance(message, dict):
                await self._ws.send(json.dumps(message))
            else:
                await self._ws.send(message)

            await self.on_send(message)

            if autocomplete:
                await self.complete()

        else:
            self._logger.debug('Failed to send message, no WebSocket Server available')

    async def complete(self):
        """Function to complete generation of a segment of audio.

        This function sends the completion token '<STOP>' to the server. This gets the server to
        generate audio up to the end of all the text sent over so far.
        """
        await self.send({'text': ' <STOP>'}, autocomplete=False)

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
        async for message in self._ws:
            if isinstance(message, str):
                message = json.loads(message)

            self._last_received_message = message
            await self.on_message(message)

            if self._play_audio:
                await self.play_audio(message)

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
        try:
            await self._create_ws_connection(ping_interval, ping_timeout)
            await self.on_open()
            await self._listen()

            if self._play_audio:
                await self.setup_pyaudio(sampling_rate=self._sampling_rate)
        except Exception as e:
            self._logger.error(f'Error opening WebSocket connection: {e}')
            await self.on_error(e)

    async def _listen(self):
        """
        Start listening to the server and handling responses.

        This function is called by the open function and should not be called directly.
        """

        async def _listen_task(client):
            if client._ws.open:  # if the client is open
                try:
                    exception = None
                    receive_task = asyncio.create_task(client._handle_message())
                    await receive_task
                except Exception as e:
                    client._logger.debug(f'Error in WebSocket process: {e}')
                    exception = e
                finally:
                    await client.close()

                    if exception:
                        await self.on_error(exception)

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

        if self._play_audio:
            await self.teardown_pyaudio()

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

    async def on_send(self, message):
        """
        Called every time a message is sent to the server.

        Parameters
        ----------
        message
            The message sent to the server.
        """
        pass
