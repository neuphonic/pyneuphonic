import asyncio
import websockets
from pyneuphonic.websocket import NeuphonicWebsocketClient
import aioconsole


class AudioForwarder(NeuphonicWebsocketClient):
    def __init__(self, target_url='ws://your-target-websocket-url', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_url = target_url

    async def on_open(self):
        self.target_ws = await websockets.connect(self.target_url)

    async def on_message(self, message: dict):
        await self.target_ws.send(message['data']['audio'])

    async def on_close(self):
        await self.target_ws.close()


async def user_input_loop(client: NeuphonicWebsocketClient):
    """Define an async function to wait for user input, in a non-blocking manner."""
    while True:
        user_text = await aioconsole.ainput("Enter text to speak (or 'quit' to exit): ")
        if user_text.lower() == 'quit':
            break
        await client.send(user_text, autocomplete=True)


async def speak():
    client = AudioForwarder(target_url='ws://your-target-websocket-url')

    await client.open()
    await user_input_loop(client)
    await client.close()


if __name__ == '__main__':
    asyncio.run(speak())
