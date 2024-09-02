import asyncio
from pyneuphonic.websocket import NeuphonicWebsocketClient
import pyaudio
from base64 import b64decode


async def setup_pyaudio(self: NeuphonicWebsocketClient):
    self.audio_player = pyaudio.PyAudio()  # create the PyAudio player

    # start the audio stream, which will play audio as and when required
    self.stream = self.audio_player.open(
        format=pyaudio.paInt16, channels=1, rate=44100, output=True
    )


async def play_audio(self: NeuphonicWebsocketClient, message: dict):
    audio_bytes = b64decode(message['data']['audio'])
    self.stream.write(audio_bytes)  # type: ignore[attr-defined]


async def teardown_pyaudio(self: NeuphonicWebsocketClient):
    self.stream.stop_stream()  # type: ignore[attr-defined]
    self.stream.close()  # type: ignore[attr-defined]
    self.audio_player.terminate()  # type: ignore[attr-defined]


async def main():
    client = NeuphonicWebsocketClient(
        on_open=setup_pyaudio,
        on_message=play_audio,
        on_close=teardown_pyaudio,
        play_audio=False,
    )

    await client.open()  # open websocket connection
    await client.send('Nice to meet you!', autocomplete=True)  # send text to server
    await asyncio.sleep(3)  # wait for callbacks to finish
    await client.close()  # close the connection


if __name__ == '__main__':
    asyncio.run(main())
