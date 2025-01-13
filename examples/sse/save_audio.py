from pyneuphonic import Neuphonic, save_audio
import os


def main():
    client = Neuphonic(api_key=os.environ.get('NEUPHONIC_API_TOKEN'))
    sse = client.tts.SSEClient()

    response = sse.send('Hello, world! This is an example of saving audio to a file.')
    audio_bytes = bytearray()

    for item in response:
        audio_bytes += item.data.audio

    save_audio(audio_bytes=audio_bytes, file_path='output.wav')


if __name__ == '__main__':
    main()
