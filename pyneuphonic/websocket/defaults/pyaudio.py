import pyaudio
import asyncio


async def setup_audio_player(self):
    # Set up an audio queue
    self.audio_queue = asyncio.Queue()

    # Set up PyAudio as the audio player
    self.audio_player = pyaudio.PyAudio()

    # Start a stream to output the audio
    self.stream = self.audio_player.open(
        format=pyaudio.paInt16, channels=1, rate=22000, output=True
    )

    # Start the audio playing task
    self.audio_task = asyncio.create_task(play_audio(self))


async def teardown_audio_player(self):
    # Stop the audio output stream
    self.stream.stop_stream()
    self.stream.close()

    # Terminate the PyAudio instance and wait for the task to finish
    self.audio_player.terminate()
    await self.audio_queue.put(None)
    await self.audio_task


async def on_audio_message(self, message: bytes):
    await self.audio_queue.put(message)


async def play_audio(self):
    buffer = b''

    while True:
        try:
            audio_data = await self.audio_queue.get()

            if audio_data is None:
                break

            buffer += audio_data

            while len(buffer) >= 4096:
                self.stream.write(buffer[:4096])
                buffer = buffer[4096:]
        except asyncio.QueueEmpty:
            pass

    if len(buffer) > 0:
        self.stream.write(buffer)


# async def play_audio(self):
#     print(1)
#     buffer = b''
#
#     while True:
#         print(2)
#         try:
#             print(3)
#             audio_data = await self.audio_queue.get()
#
#             print(3.5)
#             if audio_data is None:
#                 print(4)
#                 break
#
#             buffer += audio_data
#
#             while len(buffer) >= 4096:
#                 self.stream.write(buffer[:4096])
#                 buffer = buffer[4096:]
#         except queue.Empty:
#             print(5)
#             pass
#
#     print(6)
#     if len(buffer) > 0:
#         print(7)
#         self.stream.write(buffer)
