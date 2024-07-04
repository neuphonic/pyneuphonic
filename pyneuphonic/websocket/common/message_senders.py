from typing import AsyncGenerator
from pyneuphonic.websocket import NeuphonicWebsocketClient
from pyneuphonic.websocket.libs import split_text


async def send_async_generator(
    client: NeuphonicWebsocketClient, text_generator: AsyncGenerator
):
    """Helper function to piecewise send text from an AsyncGenerator."""
    async for text in text_generator:
        await client.send_message(text)


async def send_string(client: NeuphonicWebsocketClient, text: str):
    """Helper function to piecewise send string from an AsyncGenerator."""
    for word in split_text(text):
        await client.send_message(word)
