"""
This module contains helper functions for sending messages to a NeuphonicWebsocketClient instance. Use these
functions however you need them.
"""

from typing import AsyncGenerator
from pyneuphonic.websocket import NeuphonicWebsocketClient


async def send_async_generator(
    client: NeuphonicWebsocketClient, text_generator: AsyncGenerator
):
    """
    Helper function to send text from an async generator to a websocket client.

    Parameters
    ----------
    client
        The NeuphonicWebsocketClient instance to send text to.
    text_generator
        An async generator that yields text to be sent to the client. For example, this may be the output of an LLM
        model generating text responses to user input.
    """
    async for text in text_generator:
        await client.send(text)
