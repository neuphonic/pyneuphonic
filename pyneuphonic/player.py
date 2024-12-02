import wave
from typing import Union, Optional, Iterator, AsyncIterator
from pyneuphonic.models import SSEResponse


def save_audio(
    audio_bytes: bytes,
    file_path: str,
    sample_rate: Optional[int] = 22050,
):
    """
    Takes in an audio buffer and saves it to a .wav file.

    Parameters
    ----------
    audio_bytes
        The audio buffer to save. This is all the bytes returned from the server.
    file_path
        The file path you want to save the audio to.
    sample_rate
        The sample rate of the audio you want to save. Default is 22050.
    """
    with wave.open(file_path, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(bytes(audio_bytes))


class AudioPlayer:
    """Handles audio playback and audio exporting."""

    def __init__(self, sampling_rate: int = 22050):
        """
        Initialize with a default sampling rate.

        Parameters
        ----------
        sampling_rate : int
            The sample rate for audio playback.
        """
        self.sampling_rate = sampling_rate
        self.audio_player = None
        self.stream = None
        self.audio_bytes = bytearray()

    def open(self):
        """Open the audio stream for playback. `pyaudio` must be installed."""
        try:
            import pyaudio
        except ModuleNotFoundError:
            message = '`pip install pyaudio` required to use `AudioPlayer`'
            raise ModuleNotFoundError(message)

        self.audio_player = pyaudio.PyAudio()  # create the PyAudio player

        # start the audio stream, which will play audio as and when required
        self.stream = self.audio_player.open(
            format=pyaudio.paInt16, channels=1, rate=self.sampling_rate, output=True
        )

    def play(self, data: Union[bytes, Iterator[SSEResponse]]):
        """
        Play audio data or automatically stream over SSE responses and play the audio.

        Parameters
        ----------
        data : Union[bytes, Iterator[SSEResponse]]
            The audio data to play, either as bytes or an iterator of SSEResponse.
        """
        if isinstance(data, bytes):
            if self.stream:
                self.stream.write(data)

            self.audio_bytes += data
        elif isinstance(data, Iterator):
            for message in data:
                if not isinstance(message, SSEResponse):
                    raise ValueError(
                        '`data` must be an Iterator yielding an object of type'
                        '`pyneuphonic.models.SSEResponse`'
                    )

                self.play(message.data.audio)
        else:
            raise TypeError(
                '`data` must be of type bytes or an Iterator of SSEResponse'
            )

    async def play_async(self, data: Union[bytes, AsyncIterator[SSEResponse]]):
        """
        Asynchronously play audio data or automatically stream over SSE responses and play the audio.

        Parameters
        ----------
        data : Union[bytes, AsyncIterator[SSEResponse]]
            The audio data to play, either as bytes or an async iterator of SSEResponse.
        """
        if isinstance(data, bytes):
            self.play(data)
        elif isinstance(data, AsyncIterator):
            async for message in data:
                if not isinstance(message, SSEResponse):
                    raise ValueError(
                        '`data` must be an AsyncIterator yielding an object of type'
                        '`pyneuphonic.models.SSEResponse`'
                    )

                self.play(message.data.audio)
        else:
            raise TypeError(
                '`data` must be of type bytes or an AsyncIterator of SSEResponse'
            )

    def close(self):
        """Close the audio stream and terminate resources."""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        if self.audio_player:
            self.audio_player.terminate()
            self.audio_player = None

    def save_audio(
        self,
        file_path: str,
        sample_rate: Optional[int] = 22050,
    ):
        """Saves the audio using pynuephonic.save_audio"""
        save_audio(
            audio_bytes=self.audio_bytes, sample_rate=sample_rate, file_path=file_path
        )

    def __enter__(self):
        """Enter the runtime context related to this object."""
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context related to this object."""
        self.close()

    def __del__(self):
        """Ensure resources are released upon deletion."""
        self.close()
