from pyneuphonic.websocket import NeuphonicWebsocketClient
from pyneuphonic.websocket.libs import SubscriptableAsyncByteArray

# NOTE this needs to be manually installed
import pyaudio


async def on_open(self: NeuphonicWebsocketClient):
    """Create PyAudio resources when the websocket opens."""
    self.audio_player = pyaudio.PyAudio()  # create the PyAudio player
    self.audio_buffer = (
        SubscriptableAsyncByteArray()
    )  # create a container to store all the incoming audio bytes

    # subscribe to updates, so that we can play the audio as and when it arrives
    self.audio_buffer.subscribe(await on_audio_buffer_update(self))

    # start the audio stream, which will play audio as and when required
    self.stream = self.audio_player.open(
        format=pyaudio.paInt16, channels=1, rate=22000, output=True
    )


async def on_audio_message(self: NeuphonicWebsocketClient, message: bytes):
    """Append audio byte data to the audio_buffer"""
    await self.audio_buffer.extend(message)  # type: ignore[attr-defined]


async def on_close(self: NeuphonicWebsocketClient):
    """Close the PyAudio resources opened up by on_open"""
    self.stream.stop_stream()  # type: ignore[attr-defined]
    self.stream.close()  # type: ignore[attr-defined]
    self.audio_player.terminate()  # type: ignore[attr-defined]
    self.logger.debug('Terminated PyAudio resources.')


async def on_audio_buffer_update(self: NeuphonicWebsocketClient):
    """
    Closure function to generate callback used by the audio_buffer object. The closure is required to give the actual
    callback `_on_audio_buffer_update` access to the PyAudio resources to play the audio.
    """

    async def _on_audio_buffer_update(audio_bytes: bytes):
        self.stream.write(audio_bytes)  # type: ignore[attr-defined]

    return _on_audio_buffer_update
