import wave
from typing import Optional


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
    def __init__(self, sampling_rate: int = 22050):
        self.sampling_rate = sampling_rate
        self.audio_player = None
        self.stream = None
        self.audio_bytes = bytearray()

    def open(self):
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

    def play(self, audio_bytes: bytes):
        if self.stream:
            self.stream.write(audio_bytes)

        self.audio_bytes += audio_bytes

    def close(self):
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

    # Copy the docstring over from save_audio to AudioPlayer.save_audio
    save_audio.__doc__ = globals()['save_audio'].__doc__

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __del__(self):
        self.close()
