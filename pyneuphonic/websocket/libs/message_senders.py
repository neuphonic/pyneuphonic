"""
This module contains helper functions for sending messages with a NeuphonicWebsocketClient instance. Use these
functions however you need them.
"""

from typing import AsyncGenerator
import asyncio


async def send_async_generator(client, text_generator: AsyncGenerator):
    """
    Helper function to send text from an async generator to a websocket client. See an example of this in
    `snippets/llama3_interactive.py`.

    Parameters
    ----------
    client : pyneuphonic.websocket.NeuphonicWebsocketClient
        The NeuphonicWebsocketClient instance to send text to.
    text_generator
        An async generator that yields text to be sent to the client. For example, this may be the output of an LLM
        model generating text responses to user input.
    """
    async for text in text_generator:
        await client.send(text)
        await asyncio.sleep(0.005)

    await client.complete()
