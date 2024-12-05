from typing import Optional
import httpx

from pyneuphonic._endpoint import Endpoint
from pyneuphonic._websocket import AsyncAgentWebsocketClient


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
        return AsyncAgentWebsocketClient(api_key=self._api_key, base_url=self._base_url)
