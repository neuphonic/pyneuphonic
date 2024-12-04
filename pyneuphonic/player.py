import wave
from typing import Union, Optional, Iterator, AsyncIterator
from pyneuphonic.models import APIResponse, TTSResponse
import asyncio
from base64 import b64encode

try:
    import pyaudio
except ModuleNotFoundError:
    message = (
        '`pip install pyaudio` required to use any `pyneuphonic.player` resources.'
    )
    raise ModuleNotFoundError(message)


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
        self.audio_player = pyaudio.PyAudio()  # create the PyAudio player

        # start the audio stream, which will play audio as and when required
        self.stream = self.audio_player.open(
            format=pyaudio.paInt16, channels=1, rate=self.sampling_rate, output=True
        )

    def play(self, data: Union[bytes, Iterator[APIResponse[TTSResponse]]]):
        """
        Play audio data or automatically stream over SSE responses and play the audio.

        Parameters
        ----------
        data : Union[bytes, Iterator[TTSResponse]]
            The audio data to play, either as bytes or an iterator of TTSResponse.
        """
        if isinstance(data, bytes):
            if self.stream:
                self.stream.write(data)

            self.audio_bytes += data
        elif isinstance(data, Iterator):
            for message in data:
                if not isinstance(message, APIResponse[TTSResponse]):
                    raise ValueError(
                        '`data` must be an Iterator yielding an object of type'
                        '`pyneuphonic.models.APIResponse[TTSResponse]`'
                    )

                self.play(message.data.audio)
        else:
            raise TypeError(
                '`data` must be of type bytes or an Iterator of APIResponse[TTSResponse]'
            )

    async def play_async(
        self, data: Union[bytes, AsyncIterator[APIResponse[TTSResponse]]]
    ):
        """
        DEPRECATED. This function has been deprecated in favour of AsyncAudioPlayer.

        Asynchronously play audio data or automatically stream over SSE responses and play the audio.

        Parameters
        ----------
        data : Union[bytes, AsyncIterator[APIResponse[TTSResponse]]]
            The audio data to play, either as bytes or an async iterator of APIResponse[TTSResponse].
        """
        if isinstance(data, bytes):
            self.play(data)
        elif isinstance(data, AsyncIterator):
            async for message in data:
                if not isinstance(message, APIResponse[TTSResponse]):
                    raise ValueError(
                        '`data` must be an AsyncIterator yielding an object of type'
                        '`pyneuphonic.models.APIResponse[TTSResponse]`'
                    )

                self.play(message.data.audio)
        else:
            raise TypeError(
                '`data` must be of type bytes or an AsyncIterator of APIResponse[TTSResponse]'
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


class AsyncAudioPlayer(AudioPlayer):
    def __init__(self, sampling_rate: int = 22050):
        super().__init__(sampling_rate)

    async def open(self):
        super().open()

    async def play(self, data: Union[bytes, AsyncIterator[APIResponse[TTSResponse]]]):
        if isinstance(data, bytes):
            await asyncio.to_thread(super().play, data)
        elif isinstance(data, AsyncIterator):
            async for message in data:
                if not isinstance(message, APIResponse[TTSResponse]):
                    raise ValueError(
                        '`data` must be an AsyncIterator yielding an object of type'
                        '`pyneuphonic.models.APIResponse[TTSResponse]`'
                    )

                await self.play(message.data.audio)
        else:
            raise TypeError(
                '`data` must be of type bytes or an AsyncIterator of APIResponse[TTSResponse]'
            )

    async def close(self):
        super().close()

    async def __aenter__(self):
        """Enter the runtime context related to this object."""
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context related to this object."""
        await self.close()


class AsyncAudioRecorder:
    def __init__(self, sampling_rate: int = 16000, websocket=None):
        self.p = None
        self.stream = None
        self.sampling_rate = sampling_rate

        self._ws = websocket
        self._queue = asyncio.Queue()  # Use a queue to handle audio data asynchronously

        self._tasks = []

    async def _send(self):
        while True:
            try:
                # Wait for audio data from the queue
                data = await self._queue.get()
                await self._ws.send({'audio': b64encode(data).decode('utf-8')})
            except Exception as e:
                print(f'Error in _send: {e}')

    def _callback(self, in_data, frame_count, time_info, status):
        try:
            # Enqueue the incoming audio data for processing in the async loop
            self._queue.put_nowait(in_data)
        except asyncio.QueueFull:
            print('Audio queue is full! Dropping frames.')
        return None, pyaudio.paContinue

    async def record(self):
        self.p = pyaudio.PyAudio()

        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sampling_rate,
            input=True,
            stream_callback=self._callback,  # Use the callback function
        )

        self.stream.start_stream()  # Explicitly start the stream

        if self._ws is not None:
            send_task = asyncio.create_task(self._send())
            self._tasks.append(send_task)

    async def close(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        if self.p:
            self.p.terminate()
            self.p = None

        for task in self._tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    async def __aenter__(self):
        await self.record()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()
