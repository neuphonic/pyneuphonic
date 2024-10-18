import asyncio
import websockets

from pyneuphonic._endpoint import Endpoint
from pyneuphonic.models import AsyncWebsocketEventHandlers


class AsyncWebsocketClient(Endpoint):
    def __init__(self):
        self.event_handlers = AsyncWebsocketEventHandlers()
        self.message_queue = asyncio.Queue()
        self._ws = None
        self._tasks = []

    def on(self, event, handler):
        if event not in AsyncWebsocketEventHandlers.model_fields:
            raise ValueError(f'Event "{event}" is not a valid event.')

        setattr(self.event_handlers, event, handler)

    async def open(self):
        self._ws = await websockets.connect(self.uri, **self.kwargs)

        if self.event_handlers.open is not None:
            await self.event_handlers.open()

        receive_task = asyncio.create_task(self._receive())
        self._tasks.append(receive_task)

    async def _receive(self):
        try:
            async for message in self._ws:
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

    async def send(self, message):
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
