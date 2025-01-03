import asyncio
from pyneuphonic.websocket import NeuphonicWebsocketClient


async def main():
    # create client, uses PyAudio by default as `play_audio=True` by default
    client = NeuphonicWebsocketClient()

    await client.open()  # open websocket connection
    await client.send('Nice to meet you!', autocomplete=True)  # send text to server
    await asyncio.sleep(3)  # wait for callbacks to finish
    await client.close()  # close the connection


if __name__ == '__main__':
    asyncio.run(main())
