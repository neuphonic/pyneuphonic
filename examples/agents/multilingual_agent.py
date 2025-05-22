"""
An example of a multilingual agent, using Spanish as the example language.
This can easily be changed to any other supported language by changing the lang_code and voice_id.
"""

import os
import asyncio

# See AgentConfig model for full list of parameters to configure the agent
from pyneuphonic import Neuphonic, Agent, AgentConfig  # noqa: F401


async def main():
    client = Neuphonic(api_key=os.environ.get("NEUPHONIC_API_KEY"))

    agent_id = client.agents.create(
        name="Asistente",  # Assistant
        prompt="Eres un agente español útil.",  # You are a helpful spanish agent.
        greeting="¿Cómo puedo ayudarte hoy?",  # How can I help you today?
    ).data["agent_id"]

    # All additional keyword arguments (such as `agent_id`) are passed as
    # parameters to the model. See AgentConfig model for full list of parameters.
    agent = Agent(
        client,
        agent_id=agent_id,
        lang_code="es",
        voice_id="ea66187e-eef6-4c83-a777-52d15cfdc8e2",
    )

    try:
        await agent.start()

        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await agent.stop()


asyncio.run(main())
