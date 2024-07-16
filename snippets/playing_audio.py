import asyncio
from pyneuphonic.websocket import NeuphonicWebsocketClient

# Create the client
client = NeuphonicWebsocketClient()


async def main(text: str):
    await client.open()  # open websocket connection
    await client.send(text)  # send text to server
    await asyncio.sleep(3)  # wait for callbacks to finish
    await client.close()  # close the connection


if __name__ == '__main__':
    # Run the client
    text = 'Nice to meet you!'
    asyncio.run(main(text))
