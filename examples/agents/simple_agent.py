import os
import asyncio

# See AgentConfig model for full list of parameters to configure the agent
from pyneuphonic import Neuphonic, Agent, AgentConfig  # noqa: F401


async def main():
    client = Neuphonic(api_key=os.environ.get('NEUPHONIC_API_KEY'))

    agent_id = client.agents.create(
        name='Agent 1',
        prompt='You are a helpful agent. Answer in 10 words or less.',
        greeting='Hi, how can I help you today?',
    ).data['agent_id']

    # All additional keyword arguments (such as `agent_id`) are passed as
    # parameters to the model. See AgentConfig model for full list of parameters.
    agent = Agent(client, agent_id=agent_id)

    try:
        await agent.start()

        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await agent.stop()


asyncio.run(main())
