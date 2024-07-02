from typing import AsyncGenerator
import asyncio


async def string_to_async_generator(text: str, chunk_size=50) -> AsyncGenerator:
    """
    Split the text into chunks and yield them asynchronously. This simulates the response from an LLM.

    Parameters
    ----------
    text : str
        The text to split.
    chunk_size : int
        The size of each chunk to split it into.

    Returns
    -------
    AsyncGenerator
        An async generator object that yields string chunks and mimics an LLM producing text.
    """
    for i in range(0, len(text), chunk_size):
        yield text[i : i + chunk_size]
        await asyncio.sleep(0.001)  # Small delay to simulate streaming
    yield '[EOS]'  # Don't forget to send the end-of-stream marker
