import asyncio
import pyaudio
import threading
import queue
import nest_asyncio
import time
import ssl
import certifi

import websockets
from websockets import WebSocketClientProtocol
from typing import Generator

nest_asyncio.apply()


class TTS:
    def __init__(self, API_TOKEN, WEBSOCKET_URL='wss://neuphonic.us/speak/en'):
        # Create the websocket_url from the given api_token
        self.api_token = API_TOKEN
        self.websocket_url = f'{WEBSOCKET_URL}/{API_TOKEN}'

        # PyAudio object used to play the generated audio
        self.pyaudio = pyaudio.PyAudio()

        # A FIFO (first-in-first-out) list of audio received from the websocket API
        self.audio_queue = queue.Queue()

        # An "event" to indicate that the current stream of text has been played
        self.end_of_audio = asyncio.Event()
        self.tts_latency_printed = asyncio.Event()

        self.first_byte_received = False
        self.send_time = None
        self.first_token_time = None
        self.text_queue = asyncio.Queue()

    def play_audio(self):
        """

        Returns
        -------

        """
        stream = self.pyaudio.open(
            format=pyaudio.paInt16, channels=1, rate=22000, output=True
        )
        buffer = b''
        while True:
            try:
                audio_data = self.audio_queue.get(timeout=1)
                if audio_data is None:
                    break
                if not self.first_byte_received:
                    self.first_byte_received = True
                    audio_latency = time.time() - self.first_token_time
                    print(f'Audio generation latency: {audio_latency:.3f} seconds')
                buffer += audio_data
                while len(buffer) >= 4096:
                    stream.write(buffer[:4096])
                    buffer = buffer[4096:]
            except queue.Empty:
                if self.end_of_audio.is_set() and self.audio_queue.empty():
                    break

        if buffer:
            stream.write(buffer)

        stream.stop_stream()
        stream.close()

    async def message_handler(self, websocket: WebSocketClientProtocol):
        """
        Handles messages received from the websocket API.

        Parameters
        ----------
        websocket : WebSocketClientProtocol
            The instance of WebSocketClientProtocol returned from websockets.connect(...).
            This should be an active connection to the Neuphonic websocket api and it will yield audo

        Returns
        -------

        """
        async for message in websocket:
            if isinstance(message, bytes):
                if not self.first_byte_received:
                    self.first_byte_received = True
                    audio_latency = time.time() - self.first_token_time
                    print(f'TTS latency: {audio_latency:.3f} seconds')
                    self.tts_latency_printed.set()
                self.audio_queue.put(message)
            elif '[EOS]' in message:
                break
        self.end_of_audio.set()

    async def send_text(self, websocket: WebSocketClientProtocol, text_generator):
        """
        Sends text to the websocket API to convert the text to speech.

        Parameters
        ----------
        websocket
        text_generator

        Returns
        -------

        """
        self.send_time = time.time()
        first_token = True

        async for text in text_generator:
            if first_token:
                self.first_token_time = time.time()
                llm_latency = self.first_token_time - self.send_time
                print(f'LLM latency: {llm_latency:.3f} seconds')
                first_token = False
            await websocket.send(text)
            await self.text_queue.put(text)

        await websocket.send('[EOS]')
        await self.text_queue.put('[EOS]')

    async def print_output(self):
        await self.tts_latency_printed.wait()
        print('\033[32mResponse :: [', end='', flush=True)  # Start the response
        while True:
            text = await self.text_queue.get()
            if text == '[EOS]':
                print(']\033[0m', flush=True)  # Close the bracket and reset color
                break
            print(f'{text}', end='', flush=True)  # Print each chunk without wrapping

    async def tts(self, text_generator: Generator[str, None, None]):
        """
        Entry point for text-to-speech.

        This class will take a text generator object that yields strings, and convert these strings to audio piece by
        piece using the websocket API. It uses other class methods to play the audio and handle downstream tasks.

        Parameters
        ----------
        text_generator : Generator[str]
            The text generator object to yield strings from.

        """
        self.audio_queue = queue.Queue()  # Create a new audio queue
        self.end_of_audio.clear()  # clear Event - i.e., indicate "audio has not finished playing"
        self.first_byte_received = False
        self.tts_latency_printed.clear()  # indicate "we have not printed the latency"

        # Start the audio thread, this is run asynchronously so that it doesn't block the rest of the program
        audio_thread = threading.Thread(target=self.play_audio)
        audio_thread.start()  # start processing incoming audio, this is done in the play_audio function

        ssl_context = ssl.create_default_context(cafile=certifi.where())

        try:
            async with websockets.connect(self.websocket_url, ssl=ssl_context) as ws:
                receive_task = asyncio.create_task(self.message_handler(ws))
                send_task = asyncio.create_task(self.send_text(ws, text_generator))
                print_task = asyncio.create_task(self.print_output())
                await asyncio.wait_for(
                    asyncio.gather(send_task, receive_task, print_task), timeout=60
                )
        except Exception as e:
            print(f'Error in TTS process: {e}')
        finally:
            self.end_of_audio.set()
            self.audio_queue.put(None)
            audio_thread.join()

    def cleanup(self):
        self.pyaudio.terminate()
