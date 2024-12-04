from typing import Optional, Union, Callable
import httpx
import websockets
import json
import asyncio

from pyneuphonic._endpoint import Endpoint
from pyneuphonic.models import (
    WebsocketEventHandlers,
    AgentConfig,
    WebsocketEvents,
)


class Agents(Endpoint):
    def get(
        self,
        agent_id: Optional[str] = None,
    ):
        """
        List created agents.

        By default this endpoint returns only `id` and `name` for every agent, provide the `agent_id`
        parameter to get all the fields for a specific agent.

        Parameters
        ----------
        agent_id
            The ID of the agent to fetch. If None, fetches all agents.

        Raises
        ------
        httpx.HTTPStatusError
            If the request fails to fetch.
        """
        response = httpx.get(
            f'{self.http_url}/agents{f"/{agent_id}" if agent_id is not None else ""}',
            headers=self.headers,
            timeout=self.timeout,
        )

        self.raise_for_status(response=response, message='Failed to fetch agents.')

        return response.json()

    def create(
        self,
        name: str,
        prompt: Optional[str] = None,
        greeting: Optional[str] = None,
    ) -> dict:
        """
        Create a new agent.

        Parameters
        ----------
        name
            The name of the agent.
        prompt
            The prompt for the agent.
        greeting
            The initial greeting message for the agent.

        Raises
        ------
        httpx.HTTPStatusError
            If the request fails to create.
        """
        data = {
            'name': name,
            'prompt': prompt,
            'greeting': greeting,
        }

        response = httpx.post(
            f'{self.http_url}/agents',
            json=data,
            headers=self.headers,
            timeout=self.timeout,
        )

        self.raise_for_status(response=response, message='Failed to create agent.')

        return response.json()

    def delete(
        self,
        agent_id: str,
    ):
        """
        Delete an agent.

        Parameters
        ----------
        agent_id : str
            The ID of the agent to delete.

        Raises
        ------
        httpx.HTTPStatusError
            If the request fails to delete.
        """
        response = httpx.delete(
            f'{self.http_url}/agents/{agent_id}',
            headers=self.headers,
            timeout=self.timeout,
        )

        self.raise_for_status(response=response, message='Failed to delete agent.')

        return response.json()

    def AsyncWebsocketClient(self):
        return AsyncWebsocketClient(api_key=self._api_key, base_url=self._base_url)


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

    async def open(self, agent_config: Union[AgentConfig, dict] = AgentConfig()):
        if isinstance(agent_config, dict):
            agent_config = AgentConfig(**agent_config)

        url = f'{self.ws_url}/agents?{agent_config.to_query_params()}'

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
                    if self.event_handlers.message is not None:
                        await self.event_handlers.message(json.loads(message))
                    else:
                        await self.message_queue.put(message)
        except Exception as e:
            if self.event_handlers.error is not None:
                await self.event_handlers.error(e)
        finally:
            if self.event_handlers.close:
                await self.event_handlers.close()

            await self.close()

    async def send(self, message: Union[str, dict]):
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
