from pyneuphonic.websocket import NeuphonicWebsocketClient
from pyneuphonic.websocket.common.pyaudio import on_close, on_open, on_audio_message
from pyneuphonic.websocket.common.message_senders import send_string
import asyncio
import logging
import argparse

logging.basicConfig(
    level=logging.DEBUG, format='%(asctime)s :: %(levelname)s :: %(message)s'
)


async def speak(text: str):
    client = NeuphonicWebsocketClient(
        on_open=on_open, on_audio_message=on_audio_message, on_close=on_close
    )

    await client.open()
    await asyncio.gather(client.listen(), send_string(client, text))

    while True:
        print('hi')
        await asyncio.sleep(1)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Speak the provided text using Neuphonic'
    )
    parser.add_argument('--text', type=str, help='The text to be spoken')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    asyncio.run(speak(args.text))
