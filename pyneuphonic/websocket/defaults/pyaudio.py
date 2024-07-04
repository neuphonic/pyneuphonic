from pyneuphonic.websocket import NeuphonicSocketManager
from pyneuphonic.websocket.utils import SubscriptableByteArray
import pyaudio
import asyncio


async def on_open(self: type(NeuphonicSocketManager)):
    self.audio_player = pyaudio.PyAudio()
    self.audio_buffer = SubscriptableByteArray()
    self.audio_buffer.subscribe(await on_audio_buffer(self))
    self.is_streaming = False

    self.stream = self.audio_player.open(
        format=pyaudio.paInt16, channels=1, rate=22000, output=True
    )


async def on_audio_message(self: type(NeuphonicSocketManager), message: bytes):
    await self.audio_buffer.append(message)


async def on_close(self: type(NeuphonicSocketManager)):
    self.stream.stop_stream()
    self.stream.close()
    self.audio_player.terminate()


async def on_audio_buffer(self: type(NeuphonicSocketManager)):
    async def _on_audio_buffer(audio_bytes: bytes):
        self.stream.write(audio_bytes)
        await asyncio.sleep(0.01)

    return _on_audio_buffer
