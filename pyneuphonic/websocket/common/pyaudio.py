"""
This module contains the `PyAudio` specific callbacks for the websocket client. The callbacks are used to play audio
received from the websocket in real-time using `PyAudio`. This module implements the `on_open`, `on_message`, and `on_close`
callbacks.

All of these callbacks take the `self` parameter as the first argument, which is the NeuphonicWebsocketClient instance
to bind the callbacks to. These are treated as if they are methods of the NeuphonicWebsocketClient class.

You can see examples of these in use in the `snippets/` folder.
"""

from base64 import b64decode


async def on_open(self) -> None:
    """
    Create PyAudio resources when the websocket opens.

    This function will create the PyAudio player and the audio buffer (`SubscriptableAsyncByteArray`) to store incoming
    audio bytes. It will also start the audio stream, which will play audio in real-time when it is received.

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
        format=pyaudio.paInt16, channels=1, rate=22000, output=True
    )


async def on_message(self, message: dict):
    """
    Callback to handle incoming audio messages.

    Appends audio byte data to the audio_buffer (`SubscriptableAsyncByteArray`). This audio data is then played in
    real-time by the PyAudio stream.

    Parameters
    ----------
    self
        A NeuphonicWebsocketClient instance.
    message
        The message received from the websocket, as a dict object.
    """
    audio_bytes = b64decode(message['data']['audio'])
    self.stream.write(audio_bytes)  # type: ignore[attr-defined]


async def on_close(self):
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
