from pyneuphonic.websocket import NeuphonicWebsocketClient
import asyncio
import logging
import aioconsole

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s :: %(levelname)s :: %(message)s'
)


async def user_input_loop(client):
    """Define an async function to wait for user input, in a non-blocking manner."""
    while True:
        user_text = await aioconsole.ainput("Enter text to speak (or 'quit' to exit): ")
        if user_text.lower() == 'quit':
            break
        await client.send(user_text)


async def speak():
    client = NeuphonicWebsocketClient()

    await client.open()
    await user_input_loop(client)
    await client.close()


if __name__ == '__main__':
    asyncio.run(speak())
