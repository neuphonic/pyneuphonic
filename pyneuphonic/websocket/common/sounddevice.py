from pyneuphonic.websocket import NeuphonicWebsocketClient
from pyneuphonic.websocket.libs import SubscriptableAsyncByteArray
from base64 import b64decode

# NOTE - these need to be manually installed
import numpy as np
import sounddevice as sd


async def on_open(self: NeuphonicWebsocketClient):
    """Create sounddevice resources when the websocket opens."""
    self.audio_buffer = SubscriptableAsyncByteArray()
    self.audio_buffer.subscribe(await on_audio_buffer_update(self))

    # Start the audio stream
    sd.default.samplerate = 22000
    sd.default.channels = 1
    self.stream = sd.OutputStream(samplerate=22000, channels=1, dtype='int16')
    self.stream.start()


async def on_message(self: NeuphonicWebsocketClient, message: dict):
    """Append audio byte data to the audio_buffer"""
    audio_bytes = b64decode(message['data']['audio'])
    await self.audio_buffer.extend(audio_bytes)  # type: ignore[attr-defined]


async def on_close(self: NeuphonicWebsocketClient):
    """Close the sounddevice resources opened up by on_open"""
    self.stream.stop()  # type: ignore[attr-defined]
    self.stream.close()  # type: ignore[attr-defined]
    self._logger.debug('Terminated sounddevice resources.')


async def on_audio_buffer_update(self: NeuphonicWebsocketClient):
    """
    Closure function to generate callback used by the audio_buffer object.
    """

    async def _on_audio_buffer_update(audio_bytes: bytes):
        # Convert bytes to numpy array
        audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
        self.stream.write(audio_array)  # type: ignore[attr-defined]

    return _on_audio_buffer_update
