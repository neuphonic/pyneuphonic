import asyncio
import logging

from typing import Union, Optional, Iterator, AsyncIterator
from pyneuphonic.models import APIResponse, TTSResponse
from pyneuphonic._utils import save_audio
from base64 import b64encode
import time

try:
    import pyaudio
except ModuleNotFoundError:
    logging.warning(
        '(pyneuphonic) `pyaudio` is not installed, so audio playback and audio recording'
        ' functionality will not be enabled, and attempting to use this functionality may'
        ' throw errors. `pip install pyaudio` to resolve. This message may be ignored if'
        ' audio playback and recording features are not required.'
    )


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

        # indicates when audio will stop playing
        self._playback_end = time.perf_counter()

    @property
    def is_playing(self):
        """Returns True if there is audio currently playing."""
        return time.perf_counter() < self._playback_end

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
                duration = len(data) / (2 * self.sampling_rate)

                if self.is_playing:
                    self._playback_end += duration
                else:
                    self._playback_end = time.perf_counter() + duration

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
    def __init__(
        self, sampling_rate: int = 16000, websocket=None, player: AudioPlayer = None
    ):
        self.p = None
        self.stream = None
        self.sampling_rate = sampling_rate

        self._ws = websocket
        self.player = player
        self._queue = asyncio.Queue()  # Use a queue to handle audio data asynchronously

        self._tasks = []

    async def _send(self):
        while True:
            try:
                # Wait for audio data from the queue
                data = await self._queue.get()

                if self.player is not None and not self.player.is_playing:
                    await self._ws.send({'audio': b64encode(data).decode('utf-8')})
            except Exception as e:
                logging.error(f'Error in _send: {e}')

    def _callback(self, in_data, frame_count, time_info, status):
        try:
            # Enqueue the incoming audio data for processing in the async loop
            self._queue.put_nowait(in_data)
        except asyncio.QueueFull:
            logging.error('Audio queue is full! Dropping frames.')
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
