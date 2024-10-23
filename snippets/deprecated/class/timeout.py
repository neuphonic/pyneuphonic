from pyneuphonic.websocket import NeuphonicWebsocketClient
import asyncio
import aioconsole
import websockets


class CustomClient(NeuphonicWebsocketClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_error(self, e: Exception):
        if isinstance(e, websockets.exceptions.ConnectionClosedError):
            await self.open()


async def user_input_loop(client: NeuphonicWebsocketClient):
    """Define an async function to wait for user input, in a non-blocking manner."""
    while True:
        user_text = await aioconsole.ainput("Enter text to speak (or 'quit' to exit): ")
        if user_text.lower() == 'quit':
            break
        await client.send(user_text, autocomplete=True)


async def main():
    client = CustomClient()

    await client.open()
    await user_input_loop(client)
    await client.close()


if __name__ == '__main__':
    asyncio.run(main())
