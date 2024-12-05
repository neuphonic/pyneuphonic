import asyncio
import websockets
from typing import Callable, Union
import json
from abc import ABC, abstractmethod

from pyneuphonic._endpoint import Endpoint
from pyneuphonic.models import (
    WebsocketEventHandlers,
    TTSConfig,
    APIResponse,
    TTSResponse,
    WebsocketEvents,
    BaseConfig,
    AgentConfig,
    AgentResponse,
)
from pydantic import BaseModel


class AsyncWebsocketBase(Endpoint, ABC):
    """
    Abstract base class for asynchronous websocket clients.

    Parameters
    ----------
    api_key : str
        The API key for authentication.
    base_url : str
        The base URL for the websocket connection.
    response_type : BaseModel
        The type of response expected from the websocket. This will be one of TTSResponse and
        AgentResponse.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str,
        response_type: BaseModel,
    ):
        super().__init__(api_key=api_key, base_url=base_url)

        self.event_handlers = WebsocketEventHandlers()
        self.message_queue = asyncio.Queue()

        self._ws = None
        self._tasks = []

        self.response_type = response_type

    @abstractmethod
    def url(self, config: Union[BaseConfig, dict]) -> str:
        """
        Construct the URL for the websocket connection.

        Parameters
        ----------
        config : Union[BaseConfig, dict]
            Configuration for the websocket connection. This is required to extract the query
            parameters.

        Returns
        -------
        str
            The constructed URL. E.g.: wss://eu-west-1.api.neuphonic.com/speak/en?model=neu_hq
        """
        pass

    def on(self, event: WebsocketEvents, handler: Callable):
        """
        Register an event handler for a specific websocket event.

        Parameters
        ----------
        event : WebsocketEvents
            The event to handle.
        handler : Callable
            The function to call when the event occurs.

        Raises
        ------
        ValueError
            If the event is not a valid WebsocketEvents.
        """
        if event not in WebsocketEvents:
            raise ValueError(f'Event "{event}" is not a valid event.')

        setattr(self.event_handlers, event.value, handler)

    @abstractmethod
    async def open(self, config: Union[BaseConfig, dict]):
        """
        Open the websocket connection. After this function is called, the websocket will start
        listening and sending requests.

        Parameters
        ----------
        config : Union[BaseConfig, dict]
            Configuration for the websocket connection.
        """
        self._ws = await websockets.connect(
            self.url(config),
            ssl=self.ssl_context,
            extra_headers=self.headers,
        )

        if self.event_handlers.open is not None:
            await self.event_handlers.open()

        receive_task = asyncio.create_task(self._receive())
        self._tasks.append(receive_task)

    async def _receive(self):
        """
        Receive messages from the websocket and handle them. This is created and launched as an
        async task when when self.open is called.
        """
        try:
            async for message in self._ws:
                if isinstance(message, str):
                    message = APIResponse[self.response_type](**json.loads(message))

                    if self.event_handlers.message is not None:
                        await self.event_handlers.message(message)
                    else:
                        await self.message_queue.put(message)
        except Exception as e:
            if self.event_handlers.error is not None:
                await self.event_handlers.error(e)
        finally:
            if self.event_handlers.close:
                await self.event_handlers.close()

            await self.close()

    async def send(self, message: Union[str, dict], *args, **kwargs):
        """
        Send a message through the websocket.

        Parameters
        ----------
        message : Union[str, dict]
            The message to send. Must be a string or a dictionary.

        Raises
        ------
        AssertionError
            If the message is not a string or dictionary.
        """
        assert isinstance(
            message, (str, dict)
        ), 'Message must be an instance of str or dict'

        message = message if isinstance(message, str) else json.dumps(message)

        await self._ws.send(message)

    async def receive(self):
        """
        Receive a message from the message queue. This is where messages are placed if no message
        handler has been set.

        Returns
        -------
        APIResponse
            The next message in the queue.
        """
        return await self.message_queue.get()

    async def close(self):
        """
        Close the websocket connection and cancel all tasks.
        """
        for task in self._tasks:
            task.cancel()

            try:
                await task
            except asyncio.CancelledError:
                pass

        await self._ws.close()


class AsyncTTSWebsocketClient(AsyncWebsocketBase):
    """
    Asynchronous websocket client for Text-to-Speech (TTS) operations.

    Parameters
    ----------
    api_key : str
        The API key for authentication.
    base_url : str
        The base URL for the websocket connection.
    """

    def __init__(self, api_key: str, base_url: str):
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            response_type=TTSResponse,
        )

    def url(self, config: Union[TTSConfig, dict]) -> str:
        """
        See AsyncWebsocketClientBase.url
        """
        if not isinstance(config, TTSConfig):
            config = TTSConfig(**config)

        return f'{self.ws_url}/speak/{config.language_id}?{config.to_query_params()}'

    async def open(self, tts_config: Union[TTSConfig, dict] = TTSConfig()):
        """
        See AsyncWebsocketClientBase.open
        """
        await super().open(tts_config)

    async def send(self, message: Union[str, dict], autocomplete=False):
        """
        Send a message through the TTS websocket. This handles autocompletion of messages as well.

        Parameters
        ----------
        message : Union[str, dict]
            The message to send.
        autocomplete : bool, optional
            Whether to send an autocomplete '<STOP>' signal, by default False
        """
        await super().send(message=message)

        if autocomplete:
            await self._ws.send(json.dumps({'text': ' <STOP>'}))

    async def complete(self):
        """
        Send a completion signal '<STOP>' through the TTS websocket.
        """
        await self.send({'text': ' <STOP>'}, autocomplete=False)


class AsyncAgentWebsocketClient(AsyncWebsocketBase):
    """
    Asynchronous websocket client for /agents operations.

    Parameters
    ----------
    api_key : str
        The API key for authentication.
    base_url : str
        The base URL for the websocket connection.
    """

    def __init__(self, api_key: str, base_url: str):
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            response_type=AgentResponse,
        )

    def url(self, config: Union[AgentConfig, dict]) -> str:
        """
        See AsyncWebsocketClientBase.url
        """
        if not isinstance(config, AgentConfig):
            config = AgentConfig(**config)

        return f'{self.ws_url}/agents?{config.to_query_params()}'

    async def open(self, agent_config: Union[TTSConfig, dict] = AgentConfig()):
        """
        See AsyncWebsocketClientBase.open
        """
        await super().open(agent_config)
