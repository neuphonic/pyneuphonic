import asyncio
from pyneuphonic.websocket import NeuphonicWebsocketClient
from base64 import b64decode


class BasicClient(NeuphonicWebsocketClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_open(self):
        self.audio_buffer = bytearray()  # create a buffer to store audio data
        print('WebSocket connection opened')

    async def on_message(self, message: dict):
        audio_bytes = b64decode(message['data']['audio'])  # decode base64 audio data
        self.audio_buffer += audio_bytes  # append audio data to buffer
        print(f'Received audio data: {len(audio_bytes)} bytes')

    async def on_close(self):
        print('WebSocket connection closed.')


async def main():
    # Create the client and pass in our callbacks
    client = BasicClient(
        play_audio=False  # turn off the default audio playback
    )

    await client.open()  # open the connection
    await client.send('Hello, Neuphonic!', autocomplete=True)  # send a message
    await asyncio.sleep(1)  # wait for callbacks to finish
    await client.close()  # close the connection


# Run the client
asyncio.run(main())
