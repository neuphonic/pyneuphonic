from pyneuphonic import TTSStreamer
from pyneuphonic.utils import string_to_async_generator

import asyncio
import logging

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s :: %(levelname)s :: %(message)s'
)


async def speak(text: str):
    text_generator = string_to_async_generator(text)
    tts = TTSStreamer()

    # run the streamer
    asyncio.run(asyncio.wait_for(tts.stream(text_generator), timeout=60))
