from pyneuphonic.websocket import NeuphonicWebsocketClient
from pyneuphonic.websocket.common.pyaudio import on_close, on_open, on_message
import asyncio
import aioconsole


async def user_input_loop(client):
    """Define an async function to wait for user input, in a non-blocking manner."""
    while True:
        user_text = await aioconsole.ainput("Enter text to speak (or 'quit' to exit): ")
        if user_text.lower() == 'quit':
            break
        await client.send(user_text)


async def speak():
    client = NeuphonicWebsocketClient(
        on_open=on_open, on_message=on_message, on_close=on_close
    )

    await client.open()
    await client.listen()
    await user_input_loop(client)
    await client.close()


if __name__ == '__main__':
    asyncio.run(speak())
