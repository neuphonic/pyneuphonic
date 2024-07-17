import asyncio
from pyneuphonic.websocket import NeuphonicWebsocketClient

# create client, uses PyAudio by default if no callbacks are provided and PyAudio is installed
client = NeuphonicWebsocketClient()


async def main():
    await client.open()  # open websocket connection
    await client.send('Nice to meet you!')  # send text to server
    await asyncio.sleep(3)  # wait for callbacks to finish
    await client.close()  # close the connection


# Run the client
asyncio.run(main())
