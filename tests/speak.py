from pyneuphonic import TTSStreamer
from pyneuphonic.utils import string_to_async_generator

import argparse
import asyncio
import logging

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s :: %(levelname)s :: %(message)s'
)


if __name__ == '__main__':
    # parse the text argument
    parser = argparse.ArgumentParser()
    parser.add_argument('--text', help='The text to speak.', required=True)
    args = parser.parse_args()
    text = args.text

    # create the async text generator
    text_generator = string_to_async_generator(text)
    tts = TTSStreamer()

    # run the streamer
    asyncio.run(asyncio.wait_for(tts.stream(text_generator), timeout=60))
