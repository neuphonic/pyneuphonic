import asyncio
from pyneuphonic.websocket import NeuphonicWebsocketClient


async def main():
    # set the speed parameter to 1.4 for faster playback speed
    client = NeuphonicWebsocketClient(params={'speed': 1.4})

    await client.open()  # open websocket connection
    await client.send('Nice to meet you!', autocomplete=True)  # send text to server
    await asyncio.sleep(3)  # wait for callbacks to finish
    await client.close()  # close the connection


if __name__ == '__main__':
    asyncio.run(main())
