from pyneuphonic.websocket import NeuphonicWebsocketClient
from pyneuphonic.websocket.common.pyaudio import on_close, on_open, on_message
from pyneuphonic.websocket.common.message_senders import send_string
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
        await send_string(client, user_text)


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
