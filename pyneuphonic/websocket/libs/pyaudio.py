"""
This module contains the `PyAudio` specific callbacks for the websocket client.

These are automatically used when the `play_audio` parameter on the `NeuphonicWebsocketClient` is set to `True` which
is the default value.
These functions are called on open (`setup_pyaudio`), on message (`play_audio`) and on close (`teardown_pyaudio`) of the
websocket client.
PyAudio must be installed to use these functions, otherwise if `play_audio` is set to `True` and PyAudio is not installed
then a warning will be raised.
"""

from base64 import b64decode


async def setup_pyaudio(self, sampling_rate=22050) -> None:
    """
    Create PyAudio resources needed to play audio, when the websocket opens.

    Parameters
    ----------
    self
        A NeuphonicWebsocketClient instance.
    """
    try:
        import pyaudio
    except ModuleNotFoundError:
        message = (
            '`pip install pyaudio` required to play audio using functions in '
            '`pyneuphonic.websocket.common.pyaudio`.'
        )
        raise ModuleNotFoundError(message)

    self.audio_player = pyaudio.PyAudio()  # create the PyAudio player

    # start the audio stream, which will play audio as and when required
    self.stream = self.audio_player.open(
        format=pyaudio.paInt16, channels=1, rate=sampling_rate, output=True
    )


async def play_audio(self, message: dict):
    """
    Callback to handle incoming audio messages.

    Appends audio byte data to the open PyAudio stream to play the audio in real-time.

    Parameters
    ----------
    self
        A NeuphonicWebsocketClient instance.
    message
        The message received from the websocket, as a dict object.
    """
    audio_bytes = b64decode(message['data']['audio'])
    self.stream.write(audio_bytes)  # type: ignore[attr-defined]


async def teardown_pyaudio(self):
    """
    Close the PyAudio resources opened up by on_open.

    This function will stop the audio stream and close the PyAudio player, freeing up the resources used by PyAudio.

    Parameters
    ----------
    self
        A NeuphonicWebsocketClient instance.
    """
    self.stream.stop_stream()  # type: ignore[attr-defined]
    self.stream.close()  # type: ignore[attr-defined]
    self.audio_player.terminate()  # type: ignore[attr-defined]
    self._logger.debug('Terminated PyAudio resources.')
