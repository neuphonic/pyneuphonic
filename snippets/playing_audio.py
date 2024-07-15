import asyncio
from pyneuphonic.websocket import NeuphonicWebsocketClient
from pyneuphonic.websocket.common.pyaudio import on_open, on_close, on_message
# from pyneuphonic.websocket.common.sounddevice import on_open, on_close, on_message

# Create the client
client = NeuphonicWebsocketClient(
    on_open=on_open,  # set up audio resources
    on_message=on_message,  # play audio when received
    on_close=on_close,  # tear down audio resources
)


async def main():
    await client.open()  # open websocket connection
    await client.listen()  # start listening for incoming messages
    await client.send('Hello, World! My name is Neu.')  # send text to server
    await client.close()  # close the connection


# Run the client
asyncio.run(main())
