class AudioPlayer:
    def __init__(self, sampling_rate: int = 22050):
        self.sampling_rate = sampling_rate
        self.audio_player = None
        self.stream = None

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

    def close(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        if self.audio_player:
            self.audio_player.terminate()
            self.audio_player = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __del__(self):
        self.close()
