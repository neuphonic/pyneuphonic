"""
This example demonstrates how to use the /agent feature to directly interact with the websocket
endpoint. The example in examples/agents/simple_agent.py acts as a wrapper around this code.

Use this example for greater flexibility in handling events and interacting with the websocket.
"""

from pyneuphonic import Neuphonic, WebsocketEvents
from pyneuphonic.player import AsyncAudioPlayer, AsyncAudioRecorder
from pyneuphonic.models import APIResponse, AgentResponse, AgentConfig

import os
import asyncio


async def main():
    client = Neuphonic(api_key=os.environ.get('NEUPHONIC_API_KEY'))

    ws = client.agents.AsyncWebsocketClient()
    player = AsyncAudioPlayer()

    # passing in the websocket object will automatically forward audio to the server
    # passing in the player will ensure that the recorder is paused while the speaker is playing
    # sampling_rate=16000 is used for quicker speech recognition
    recorder = AsyncAudioRecorder(sampling_rate=16000, websocket=ws, player=player)

    async def on_message(message: APIResponse[AgentResponse]):
        # server will return 3 types of messages: audio_response, user_transcript, llm_response
        if message.data.type == 'audio_response':
            await player.play(message.data.audio)
        elif message.data.type == 'user_transcript':
            print(f'User: {message.data.text}')
        elif message.data.type == 'llm_response':
            print(f'Agent: {message.data.text}')

    async def on_close():
        await player.close()
        await recorder.close()

    ws.on(WebsocketEvents.MESSAGE, on_message)
    ws.on(WebsocketEvents.CLOSE, on_close)

    await player.open()
    await ws.open(agent_config=AgentConfig(sampling_rate=16000))
    await recorder.record()

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await ws.close()


asyncio.run(main())
