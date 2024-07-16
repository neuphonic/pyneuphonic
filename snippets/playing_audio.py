import asyncio
from pyneuphonic.websocket import NeuphonicWebsocketClient


async def main(text: str):
    client = NeuphonicWebsocketClient()  # Create the client
    await client.open()  # open websocket connection
    await client.send(text)  # send text to server
    await asyncio.sleep(3)  # wait for callbacks to finish
    await client.close()  # close the connection


if __name__ == '__main__':
    text = 'Nice to meet you!'  # Change this to anything you want!
    asyncio.run(main(text))
