import asyncio
import logging

from typing import Union, Iterator, AsyncIterator, Optional
from pyneuphonic.models import APIResponse, TTSResponse
from pyneuphonic._utils import save_audio
from base64 import b64encode
import time

logger = logging.getLogger('pyneuphonic')

try:
    import pyaudio
except ModuleNotFoundError:
    logger.warning(
        '`pyaudio` is not installed, so audio playback and audio recording'
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

    @staticmethod
    def _get_default_output_device_info():
        """Get the output device that pyaudio will choose by default."""
        pa = pyaudio.PyAudio()
        device_info = pa.get_default_output_device_info()
        pa.terminate()
        return device_info

    @property
    def output_device_possibly_has_echo(self):
        """Checks whether the default output device is likely to have echo based on naming heuristics."""
        output_device = AudioPlayer._get_default_output_device_info()
        device_name = output_device['name'].lower()
        keywords = ['airpods', 'headphone', 'headset', 'earbuds']

        if any(keyword in device_name for keyword in keywords):
            return False

        return True

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
    ):
        """Saves the audio using pynuephonic.save_audio"""
        save_audio(
            audio_bytes=self.audio_bytes,
            sampling_rate=self.sampling_rate,
            file_path=file_path,
        )

    def __enter__(self):
        """Enter the runtime context related to this object."""
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context related to this object."""
        self.close()


class AsyncAudioPlayer(AudioPlayer):
    """Asynchronous version of AudioPlayer that allows for smoother handling of interruptions."""

    def __init__(self, sampling_rate: int = 22050):
        super().__init__(sampling_rate)
        self.playback_task: Optional[asyncio.Task] = None
        self.playback_queue: Optional[asyncio.Queue] = asyncio.Queue()

    async def open(self):
        """Open the audio stream for playback and creates playback task. `pyaudio` must be installed."""
        super().open()
        self.playback_task = asyncio.create_task(self._playback_task())

    async def _playback_task(self):
        """The playback function that runs as a task. Grabs items off self.playback_queue and plays them using self._play."""
        while True:
            if isinstance(self.playback_queue, asyncio.Queue):
                audio_chunk = await self.playback_queue.get()
                await self._play(audio_chunk)
            else:
                raise Exception(
                    f'`audio_queue` is an invalid type: {type(self.playback_queue)}'
                )

    async def _play(self, data: Union[bytes, AsyncIterator[APIResponse[TTSResponse]]]):
        """
        Play audio data or automatically stream over SSE responses and play the audio.

        Parameters
        ----------
        data : Union[bytes, Iterator[TTSResponse]]
            The audio data to play, either as bytes or an iterator of TTSResponse.
        """
        if isinstance(data, bytes):
            CHUNK_SIZE = 2048  # chunked playback to allow responsive interruptions
            for i in range(0, len(data), CHUNK_SIZE):
                chunk = data[i : i + CHUNK_SIZE]
                if not chunk:
                    break
                await asyncio.to_thread(super().play, chunk)
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

    async def play(self, data: Union[bytes, AsyncIterator[APIResponse[TTSResponse]]]):
        """Enqueue a chunk of audio to be picked up by self._playback_task."""
        if isinstance(data, bytes):
            await self.playback_queue.put(data)
        elif isinstance(data, AsyncIterator):
            async for message in data:
                await self.playback_queue.put(message.data.audio)
        else:
            raise TypeError(
                '`data` must be of type bytes or an AsyncIterator of APIResponse[TTSResponse]'
            )

    async def close(self):
        """Stop audio playback immediately and close all pyaudio resources."""
        await self.stop_playback(closing=True)
        super().close()

    async def stop_playback(self, closing: bool = False):
        """Stops audio playback immediately and deletes all audio that still needs to be played, if
        the player is currently playing.

        Parameters
        ----------
        closing : bool, optional
            If True, indicates that the player is being closed and the playback task should not be
            recreated after cancellation. Default is False.
        """
        if isinstance(self.playback_task, asyncio.Task) and (
            self.is_playing or closing
        ):
            try:
                self.playback_task.cancel()
                await self.playback_task
            except asyncio.CancelledError as e:
                pass
            finally:
                del self.playback_queue
                self.playback_queue = asyncio.Queue()

                if not closing:
                    self.playback_task = asyncio.create_task(self._playback_task())

    async def __aenter__(self):
        """Enter the runtime context related to this object."""
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context related to this object."""
        while self.is_playing:
            # Wait until all audio has finished playing before terminating audio player
            await asyncio.sleep(1)

        await self.close()


class AsyncAudioRecorder:
    def __init__(
        self,
        sampling_rate: int = 16000,
        websocket=None,
        player: AudioPlayer = None,
        allow_interruptions: Optional[bool] = None,
    ):
        """
        Initialize the AsyncAudioRecorder.

        Parameters
        ----------
        sampling_rate : int, optional
            The sampling rate for audio recording, by default 16000.
        websocket : object, optional
            Websocket client for sending audio data, by default None.
        player : AudioPlayer, optional
            Audio player instance that may be used for playback, by default None.
        allow_interruptions : bool or None, optional
            Whether to allow recording while playing audio, by default None and is determined based
            on devices default output device. If the output device is a headset, then
            allow_interruptions will be set to True as there will be no echo.
        """
        self.p = None
        self.stream = None
        self.sampling_rate = sampling_rate

        self._ws = websocket
        self.player = player
        self._queue = asyncio.Queue()  # Use a queue to handle audio data asynchronously

        self._tasks = []

        if isinstance(player, (AudioPlayer, AsyncAudioPlayer)):
            if allow_interruptions is None:
                self.allow_interruptions = (
                    not self.player.output_device_possibly_has_echo
                )
            else:
                self.allow_interruptions = allow_interruptions

            if self.player.output_device_possibly_has_echo and self.allow_interruptions:
                logger.warning(
                    'You have set allow_interruptions=True on AsyncAudioRecorder but your output device '
                    f'"{AudioPlayer._get_default_output_device_info()["name"]}" is not a headset. '
                    'This may cause audio feedback or echo when recording while playing audio.'
                )
            elif not self.allow_interruptions:
                logger.warning(
                    'Audio interruptions are disabled (allow_interruptions=False on AsyncAudioRecorder). '
                    'This setting was either explicitly configured or automatically determined based on your output device. '
                    'When audio is playing, microphone input will be disabled to prevent echo, meaning '
                    'you cannot interrupt the agent while it is speaking. To enable interruptions, use earphones.'
                )

    async def _send(self):
        while True:
            try:
                # Wait for audio data from the queue
                data = await self._queue.get()

                if self.player is not None and (
                    not self.player.is_playing or self.allow_interruptions
                ):
                    await self._ws.send({'audio': b64encode(data).decode('utf-8')})
            except Exception as e:
                logger.error(f'Error in _send: {e}')

    def _callback(self, in_data, frame_count, time_info, status):
        try:
            # Enqueue the incoming audio data for processing in the async loop
            self._queue.put_nowait(in_data)
        except asyncio.QueueFull:
            logger.error('Audio queue is full! Dropping frames.')
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
