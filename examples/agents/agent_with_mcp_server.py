"""
This example illustrates how to create and run an agent with an MCP server attached to it.
"""

import os
import asyncio

# See AgentConfig model for full list of parameters to configure the agent
from pyneuphonic import Neuphonic, Agent, AgentConfig  # noqa


async def main():
    client = Neuphonic(api_key=os.environ.get('NEUPHONIC_API_KEY'))

    agent_id = client.agents.create(
        name='Agent 1',
        prompt='You are a helpful agent. Answer in 10 words or less.',
        greeting='Hi, how can I help you today?',
    ).data['agent_id']

    # Pass your ngrok URL into the Agent, or whichever URL is hosting your MCP server
    agent = Agent(
        client,
        agent_id=agent_id,
        mcp_servers=['https://1234-56-789-123-4.ngrok-free.app/sse'],
    )

    try:
        await agent.start()

        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await agent.stop()


asyncio.run(main())
