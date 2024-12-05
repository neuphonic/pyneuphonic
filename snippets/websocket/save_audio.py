from pyneuphonic import Neuphonic, WebsocketEvents, save_audio
from pyneuphonic.models import APIResponse, TTSResponse
import os
import asyncio


async def main():
    client = Neuphonic(api_key=os.environ.get('NEUPHONIC_API_TOKEN'))

    ws = client.tts.AsyncWebsocketClient()
    audio_bytes = bytearray()

    # Attach event handlers. Check WebsocketEvents enum for all valid events.
    async def on_message(message: APIResponse[TTSResponse]):
        # add the audio we recieve to the bytearray so we can save it later
        nonlocal audio_bytes
        audio_bytes += message.data.audio

    ws.on(WebsocketEvents.MESSAGE, on_message)  # attach the event handler

    await ws.open()
    await ws.send(
        'Hello, world! This is an example of saving audio to a file.', autocomplete=True
    )
    await asyncio.sleep(3)  # wait until we recieve all of the messages from the server
    await ws.close()  # close the websocket

    # save audio to a file
    save_audio(audio_bytes=audio_bytes, file_path='output.wav')


asyncio.run(main())
