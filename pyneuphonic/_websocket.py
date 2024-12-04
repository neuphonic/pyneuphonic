import asyncio
import websockets
from typing import Callable, Union
import json
from abc import ABC, abstractmethod

from pyneuphonic._endpoint import Endpoint
from pyneuphonic.models import (
    WebsocketEventHandlers,
    TTSConfig,
    WebsocketResponse,
    TTSResponse,
    WebsocketEvents,
    BaseConfig,
    AgentConfig,
    AgentResponse,
)
from pydantic import BaseModel


class AsyncWebsocketBase(Endpoint, ABC):
    def __init__(
        self,
        api_key: str,
        base_url: str,
        config: Union[BaseConfig, dict],
        response_type: BaseModel,
    ):
        super().__init__(api_key=api_key, base_url=base_url)

        self.event_handlers = WebsocketEventHandlers()
        self.message_queue = asyncio.Queue()

        self._ws = None
        self._tasks = []
        self.config = config
        self.response_type = response_type

    @property
    @abstractmethod
    def url(self) -> str:
        pass

    def on(self, event: WebsocketEvents, handler: Callable):
        if event not in WebsocketEvents:
            raise ValueError(f'Event "{event}" is not a valid event.')

        setattr(self.event_handlers, event.value, handler)

    async def open(self):
        self._ws = await websockets.connect(
            self.url,
            ssl=self.ssl_context,
            extra_headers=self.headers,
        )

        if self.event_handlers.open is not None:
            await self.event_handlers.open()

        receive_task = asyncio.create_task(self._receive())
        self._tasks.append(receive_task)

    async def _receive(self):
        try:
            async for message in self._ws:
                if isinstance(message, str):
                    message = WebsocketResponse[self.response_type](
                        **json.loads(message)
                    )

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
        assert isinstance(
            message, (str, dict)
        ), 'Message must be an instance of str or dict'

        message = message if isinstance(message, str) else json.dumps(message)

        await self._ws.send(message)

    async def receive(self):
        return await self.message_queue.get()

    async def close(self):
        for task in self._tasks:
            task.cancel()

            try:
                await task
            except asyncio.CancelledError:
                pass

        await self._ws.close()


class AsyncTTSWebsocketClient(AsyncWebsocketBase):
    def __init__(
        self, api_key: str, base_url: str, tts_config: TTSConfig = TTSConfig()
    ):
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            config=tts_config,
            response_type=TTSResponse,
        )

    @property
    def url(self) -> str:
        if not isinstance(self.config, TTSConfig):
            self.config = TTSConfig(**self.config)

        return f'{self.ws_url}/speak/{self.config.language_id}?{self.config.to_query_params()}'

    async def send(self, message: Union[str, dict], autocomplete=False):
        await super().send(message=message)

        if autocomplete:
            await self._ws.send(json.dumps({'text': ' <STOP>'}))

    async def complete(self):
        await self.send({'text': ' <STOP>'}, autocomplete=False)


class AsyncAgentWebsocketClient(AsyncWebsocketBase):
    def __init__(
        self, api_key: str, base_url: str, agent_config: AgentConfig = AgentConfig()
    ):
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            config=agent_config,
            response_type=AgentResponse,
        )

    @property
    def url(self) -> str:
        return f'{self.ws_url}/agents?{self.config.to_query_params()}'
