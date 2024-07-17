import asyncio
from pyneuphonic.websocket import NeuphonicWebsocketClient
from base64 import b64decode
import wave


async def on_open(self: NeuphonicWebsocketClient):
    self.audio_buffer = bytearray()


async def on_message(self: NeuphonicWebsocketClient, message: dict):
    audio_bytes = b64decode(message['data']['audio'])
    self.audio_buffer += audio_bytes


async def on_close(self: NeuphonicWebsocketClient):
    with wave.open('output.wav', 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)  # 2 bytes per sample
        wav_file.setframerate(22000)  # 22 kHz sample rate
        wav_file.writeframes(bytes(self.audio_buffer))


async def main(text: str):
    client = NeuphonicWebsocketClient(
        on_open=on_open, on_message=on_message, on_close=on_close
    )  # create the client
    await client.open()  # open websocket connection
    await client.send(text)  # send text to server
    await asyncio.sleep(3)  # wait for callbacks to finish
    await client.close()  # close the connection


if __name__ == '__main__':
    text = 'Nice to meet you!'  # Change this to anything you want!
    asyncio.run(main(text))
