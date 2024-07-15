import asyncio
from pyneuphonic.websocket import NeuphonicWebsocketClient
from base64 import b64decode


# Define callback functions
async def on_message(self: NeuphonicWebsocketClient, message: dict):
    audio_bytes = b64decode(message['data']['audio'])
    print(f'Received audio data: {len(audio_bytes)} bytes')


async def on_open(self: NeuphonicWebsocketClient):
    print('WebSocket connection opened')


async def on_close(self: NeuphonicWebsocketClient):
    print('WebSocket connection closed')


# Create the client and pass in our callbacks
client = NeuphonicWebsocketClient(
    on_message=on_message, on_open=on_open, on_close=on_close
)


async def main():
    await client.open()  # open the connection
    await client.listen()  # start listening for incoming messages
    await client.send('Hello, Neuphonic!')  # send a message

    # close the connection, by default client.close will wait for all audio
    # to be received before terminating the connection
    await client.close()


# Run the client
asyncio.run(main())
