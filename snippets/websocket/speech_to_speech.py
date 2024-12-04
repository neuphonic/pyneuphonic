from pyneuphonic import Neuphonic, WebsocketEvents
from pyneuphonic.player import AsyncAudioPlayer, AsyncAudioRecorder

import os
import asyncio
import base64


async def main():
    client = Neuphonic(api_key=os.environ.get('NEUPHONIC_API_TOKEN'))

    ws = client.agents.AsyncWebsocketClient()
    player = AsyncAudioPlayer()
    recorder = AsyncAudioRecorder(websocket=ws)

    async def on_message(message):
        if message['data']['type'] == 'audio_response':
            await player.play(base64.b64decode(message['data']['audio']))

    async def on_close():
        await player.close()
        await recorder.close()

    ws.on(WebsocketEvents.MESSAGE, on_message)
    ws.on(WebsocketEvents.CLOSE, on_close)

    await player.open()
    await ws.open()
    await recorder.record()

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await ws.close()


asyncio.run(main())
