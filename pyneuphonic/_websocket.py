import asyncio
import websockets
from typing import Callable, Union
import json

from pyneuphonic._endpoint import Endpoint
from pyneuphonic.models import (
    WebsocketEventHandlers,
    TTSConfig,
    WebsocketResponse,
    WebsocketEvents,
)


class AsyncWebsocketClient(Endpoint):
    def __init__(
        self,
        api_key: str,
        base_url: str,
    ):
        super().__init__(api_key=api_key, base_url=base_url)

        self.event_handlers = WebsocketEventHandlers()
        self.message_queue = asyncio.Queue()

        self._ws = None
        self._tasks = []

    def on(self, event: WebsocketEvents, handler: Callable):
        if event not in WebsocketEvents:
            raise ValueError(f'Event "{event}" is not a valid event.')

        setattr(self.event_handlers, event.value, handler)

    async def open(self, tts_config: Union[TTSConfig, dict] = TTSConfig()):
        url = f'{self.ws_url}/speak/{tts_config.language_id}?{tts_config.to_query_params()}'

        self._ws = await websockets.connect(
            url,
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
                    message = WebsocketResponse(**json.loads(message))

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

    async def send(self, message: Union[str, dict], autocomplete=False):
        assert isinstance(
            message, (str, dict)
        ), 'Message must be an instance of str or dict'
        message = message if isinstance(message, str) else json.dumps(message)
        await self._ws.send(message)

        if autocomplete:
            await self._ws.send(json.dumps({'text': ' <STOP>'}))

    async def complete(self):
        await self.send({'text': ' <STOP>'}, autocomplete=False)

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
