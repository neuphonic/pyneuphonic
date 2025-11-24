from typing import Optional

from pyneuphonic._endpoint import Endpoint
from pyneuphonic._websocket import AsyncAgentWebsocketClient
from pyneuphonic.models import APIResponse  # noqa: F401


class Agents(Endpoint):
    """Manage and interact with agents."""

    def list(
        self,
    ) -> APIResponse[dict]:
        """
        List created agents.

        By default this endpoint returns only `id` and `name` for every agent, provide the `agent_id`
        parameter to get all the fields for a specific agent.

        Parameters
        ----------
        agent_id
            The ID of the agent to fetch. If None, fetches all agents.

        Returns
        -------
        APIResponse[dict]
            response.data['agent'] will be an dictionary.

        Raises
        ------
        httpx.HTTPStatusError
            If the request fails to fetch.
        """
        return super().get(endpoint="/agents", message="Failed to fetch agents.")

    def get(
        self,
        agent_id: str,
    ) -> APIResponse[dict]:
        """
        List created agents.

        By default this endpoint returns only `id` and `name` for every agent, provide the `agent_id`
        parameter to get all the fields for a specific agent.

        Parameters
        ----------
        agent_id
            The ID of the agent to fetch. If None, fetches all agents.

        Returns
        -------
        APIResponse[dict]
            response.data['agent'] will be a dictionary.

        Raises
        ------
        httpx.HTTPStatusError
            If the request fails to fetch.
        """
        return super().get(
            id=agent_id, endpoint="/agents/", message="Failed to fetch agent."
        )

    def create(
        self,
        name: str,
        prompt: Optional[str] = None,
        greeting: Optional[str] = None,
    ) -> APIResponse[dict]:
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

        Returns
        -------
        APIResponse[dict]
            response.data will contain a success message on successful creation.

        Raises
        ------
        httpx.HTTPStatusError
            If the request fails to create.
        """
        data = {
            "name": name,
            "prompt": prompt,
            "greeting": greeting,
        }

        return super().post(
            data=data, endpoint="/agents", message="Failed to create agent."
        )

    def delete(
        self,
        agent_id: str,
    ) -> APIResponse[dict]:
        """
        Delete an agent.

        Parameters
        ----------
        agent_id : str
            The ID of the agent to delete.

        Returns
        -------
        APIResponse[dict]
            response.data will contain a delete message on successful deletion.

        Raises
        ------
        httpx.HTTPStatusError
            If the request fails to delete.
        """
        return super().delete(
            id=agent_id, endpoint="/agents/", message="Failed to delete agent."
        )

    def AsyncWebsocketClient(self):
        return AsyncAgentWebsocketClient(api_key=self._api_key, base_url=self._base_url)
