from pyneuphonic import TTS
import argparse
import asyncio
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s:: %(message)s')


async def main(input_text):
    async def text_generator():
        yield input_text

    tts = TTS()

    await asyncio.wait_for(tts.tts(text_generator()), timeout=60)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--text', help='The text to speak.', required=True)
    args = parser.parse_args()
    text = args.text

    asyncio.run(main(text))
