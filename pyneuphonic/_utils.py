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
