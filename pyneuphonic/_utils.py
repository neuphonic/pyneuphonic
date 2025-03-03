import wave

from typing import Optional, Iterator, Union, AsyncIterator

from pyneuphonic.models import APIResponse, TTSResponse

def save_audio(
    audio_bytes: Union[bytes, bytearray, Iterator[APIResponse[TTSResponse]]],
    file_path: str,
    sampling_rate: Optional[int] = 22050,
):
    """
    Takes in an audio buffer and saves it to a .wav file.

    Parameters
    ----------
    audio_bytes
        The audio buffer to save. This is all the bytes returned from the server.
    file_path
        The file path you want to save the audio to.
    sampling_rate
        The sample rate of the audio you want to save. Default is 22050.
    """
    if isinstance(audio_bytes, bytes) or isinstance(audio_bytes, bytearray):
        with wave.open(file_path, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sampling_rate)
            wav_file.writeframes(bytes(audio_bytes))
    elif isinstance(audio_bytes, Iterator):
        with wave.open(file_path, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sampling_rate)
            for message in audio_bytes:
                if not isinstance(message, APIResponse[TTSResponse]):
                    raise ValueError(
                        '`audio_bytes` must be an Iterator yielding an object of type'
                        '`pyneuphonic.models.APIResponse[TTSResponse]`'
                    )
                wav_file.writeframes(message.data.audio)


async def async_save_audio(
    audio_bytes: Union[bytes, bytearray, AsyncIterator[APIResponse[TTSResponse]]],
    file_path: str,
    sampling_rate: Optional[int] = 22050,
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
    if isinstance(audio_bytes, bytes) or isinstance(audio_bytes, bytearray):
        with wave.open(file_path, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sampling_rate)
            wav_file.writeframes(bytes(audio_bytes))
    elif isinstance(audio_bytes, AsyncIterator):
        with wave.open(file_path, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sampling_rate)
            async for message in audio_bytes:
                if not isinstance(message, APIResponse[TTSResponse]):
                    raise ValueError(
                        '`audio_bytes` must be an AsyncIterator yielding an object of type'
                        '`pyneuphonic.models.APIResponse[TTSResponse]`'
                    )
                wav_file.writeframes(message.data.audio)
