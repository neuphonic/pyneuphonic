# PyNeuphonic
The official Neuphonic Python library providing simple, convenient access to the Neuphonic text-to-speech websocket
API from any Python 3.9+ application.

For support or to get involved, join our [Discord](https://discord.gg/G258vva7gZ)!

- [PyNeuphonic](#pyneuphonic)
  - [Documentation](#documentation)
    - [Installation](#installation)
    - [List Voices](#list-voices)
    - [Audio Generation](#audio-generation)
      - [SSE (Server Side Events)](#sse-server-side-events)
      - [Asynchronous SSE](#asynchronous-sse)
      - [Asynchronous Websocket](#asynchronous-websocket)
    - [Saving Audio](#saving-audio)
  - [Example Applications](#example-applications)

## Documentation
See [https://docs.neuphonic.com](https://docs.neuphonic.com) for the complete API documentation.

### Installation
Install this package into your environment using your chosen package manager:

```bash
pip install pyneuphonic
```

### List Voices
```python
from pyneuphonic import Neuphonic
import os

client = Neuphonic(api_key=os.environ.get('NEUPHONIC_API_TOKEN'))
voices = client.voices.get()  # get's all available voices
print(voices)
```

### Audio Generation
#### SSE (Server Side Events)
```python
from pyneuphonic import Neuphonic, AudioPlayer, TTSConfig
import os
import time

client = Neuphonic(api_key=os.environ.get('NEUPHONIC_API_TOKEN'))

sse = client.tts.SSEClient()

# TTSConfig is a pydantic model so check out the source code for all valid options
tts_config = TTSConfig(speed=1.05)

# Create an audio player with `pyaudio`
with AudioPlayer() as player:
    response = sse.send('Hello, world!', tts_config=tts_config)

    for item in response:
        player.play(item.data.audio)

    player.save_audio()  # save the audio to a .wav file
    time.sleep(1)  # ensure all the audio has played before the python program terminates
```

#### Asynchronous SSE
```python
from pyneuphonic import Neuphonic, AudioPlayer, TTSConfig
import os
import asyncio

async def main():
    client = Neuphonic(api_key=os.environ.get('NEUPHONIC_API_TOKEN'))

    sse = client.tts.AsyncSSEClient()
    tts_config = TTSConfig(speed=1.05)

    with AudioPlayer() as player:
        response = sse.send('Hello, world!', tts_config=tts_config)

        async for item in response:
            player.play(item.data.audio)

        player.save_audio()  # save the audio to a .wav file
        await asyncio.sleep(1)  # ensure all the audio has played before the python program terminates

asyncio.run(main())
```

#### Asynchronous Websocket
```python
from pyneuphonic import Neuphonic, AudioPlayer, TTSConfig, WebsocketEvents
from pyneuphonic.models import WebsocketResponse
import os
import asyncio

async def main():
    client = Neuphonic(api_key=os.environ.get('NEUPHONIC_API_TOKEN'))

    ws = client.tts.AsyncWebsocketClient()
    tts_config = TTSConfig(voice='ebf2c88e-e69d-4eeb-9b9b-9f3a648787a5')

    player = AudioPlayer()
    player.open()

    # Attach event handlers. Check WebsocketEvents enum for all valid events.
    async def on_message(message: WebsocketResponse):
        player.play(message.data.audio)

    async def on_close():
        player.close()

    ws.on(WebsocketEvents.MESSAGE, on_message)
    ws.on(WebsocketEvents.CLOSE, on_close)

    await ws.open(tts_config=tts_config)

    # A special symbol ' <STOP>' must be sent to the server, otherwise the server will wait for
    # more text to be sent before generating the last few snippets of audio
    await ws.send('Hello, world!', autocomplete=True)
    await ws.send('Hello, world! <STOP>')  # Both the above line, and this line, are equivalent

    await asyncio.sleep(3)  # let the audio play
    player.save_audio()  # save the audio to a .wav file
    await ws.close()  # close the websocket and terminate the audio resources

asyncio.run(main())
```

### Saving Audio
As per the examples above, you can use the `AudioPlayer` object to save audio.
```python
player.save_audio()
```
However, if you do not want to play audio and simply want to save it, check out the examples
in [snippets/sse/save_audio.py](./snippets/sse/save_audio.py) and
[snippets/websocket/save_audio.py](./snippets/websocket/save_audio.py) for examples on how to
do this.

## Example Applications
Check out the [snippets](./snippets/) folder for some example applications.
