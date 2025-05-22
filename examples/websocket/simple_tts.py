from pyneuphonic import Neuphonic, WebsocketEvents
from pyneuphonic.models import APIResponse, TTSResponse
from pyneuphonic.player import AudioPlayer
import os
import asyncio
import aioconsole


async def main():
    client = Neuphonic(api_key=os.environ.get("NEUPHONIC_API_KEY"))

    ws = client.tts.AsyncWebsocketClient()

    player = AudioPlayer()
    player.open()

    # Attach event handlers. Check WebsocketEvents enum for all valid events.
    async def on_message(message: APIResponse[TTSResponse]):
        player.play(message.data.audio)

    async def on_close():
        player.close()

    ws.on(WebsocketEvents.MESSAGE, on_message)
    ws.on(WebsocketEvents.CLOSE, on_close)

    await ws.open()

    while True:
        user_text = await aioconsole.ainput("Enter text to speak (or 'quit' to exit): ")

        if user_text.lower() == "quit":
            break

        await ws.send(user_text, autocomplete=True)

    await ws.close()  # close the websocket and terminate the audio resources


asyncio.run(main())
