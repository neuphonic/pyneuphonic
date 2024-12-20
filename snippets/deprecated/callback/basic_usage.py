import asyncio
from pyneuphonic.websocket import NeuphonicWebsocketClient
from base64 import b64decode


# Define callback functions
async def on_open(self: NeuphonicWebsocketClient):
    self.audio_buffer = bytearray()  # create a buffer to store audio data
    print('WebSocket connection opened')


async def on_message(self: NeuphonicWebsocketClient, message: dict):
    audio_bytes = b64decode(message['data']['audio'])  # decode base64 audio data
    self.audio_buffer += audio_bytes  # append audio data to buffer
    print(f'Received audio data: {len(audio_bytes)} bytes')


async def on_close(self: NeuphonicWebsocketClient):
    print('WebSocket connection closed.')


# Create the client and pass in our callbacks
client = NeuphonicWebsocketClient(
    on_open=on_open,
    on_message=on_message,
    on_close=on_close,
    play_audio=False,  # turn off the default audio playback
)


async def main():
    await client.open()  # open the connection
    await client.send('Hello, Neuphonic!', autocomplete=True)  # send a message
    await asyncio.sleep(1)  # wait for callbacks to finish
    await client.close()  # close the connection


# Run the client
asyncio.run(main())
