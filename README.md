# PyNeuphonic
The official Neuphonic Python library providing simple, convenient access to the Neuphonic text-to-speech websocket
API from any Python 3.9+ application.

For support or to get involved, join our [Discord](https://discord.gg/G258vva7gZ)!

- [PyNeuphonic](#pyneuphonic)
  - [Documentation](#documentation)
    - [Installation](#installation)
    - [Voices](#voices)
      - [Get Voices](#get-voices)
      - [Clone Voice](#clone-voice)
    - [Audio Generation](#audio-generation)
      - [SSE (Server Side Events)](#sse-server-side-events)
      - [Asynchronous SSE](#asynchronous-sse)
      - [Asynchronous Websocket](#asynchronous-websocket)
    - [Saving Audio](#saving-audio)
    - [Agents](#agents)
  - [Example Applications](#example-applications)

## Documentation
See [https://docs.neuphonic.com](https://docs.neuphonic.com) for the complete API documentation.

### Installation
Install this package into your environment using your chosen package manager:

```bash
pip install pyneuphonic
```

In most cases, you will be playing the audio returned from our servers directly on your device.
We offer utilities to play audio through your device's speakers using `pyaudio`.
To use these utilities, please also `pip install pyaudio`.

> :warning: Mac users encountering a `'portaudio.h' file not found` error can resolve it by running
> `brew install portaudio`.

### Voices

#### Get Voices

To get all available voices you can run the following snippet.

```python
from pyneuphonic import Neuphonic
import os

client = Neuphonic(api_key=os.environ.get('NEUPHONIC_API_TOKEN'))
voices = client.voices.get()  # get's all available voices
print(voices)
```


#### Clone Voice

To clone a voice based on a audio file, you can run the following snippet.

```python
from pyneuphonic import Neuphonic
import os

client = Neuphonic(api_key=os.environ.get('NEUPHONIC_API_TOKEN'))

voice_file_path = 'XXX.wav'

result = client.voices.clone(voice_name='NewNeuphonic', voice_tags=['tag1', 'tag2'], voice_file_path = voice_file_path)

print(result['data']['message'])

```

If you have successfully cloned a voice, the following message will be displayed: "Voice has successfully been cloned with ID XXXXXXX." Once cloned, you can use this voice just like any of the standard voices when calling the TTS (Text-to-Speech) service.

To view a list of all available voices (including the voices you have cloned), simply call the `client.voices.get(api_key="")` endpoint.


#### Update Voice

To update a voice which already exists, i.e. update the reference clip for a voice name you already have provided you can do as follows.

Update based on the new clip and the old name:

```python

voice_file_path = 'XXX.wav'

result = client.voices.update(voice_file_path = voice_file_path,
voice_name='NewNeuphonic')

print(result)
```


Alternatively, if you wanna provide the voice id:
```python
result = client.voices.update(voice_file_path = voice_file_path,
voice_id=XXX)

print(result)
```

#### Delete Voice

To delete a voice which already exists.

```python

voice_file_path = 'XXX.wav'

result = client.voices.update(voice_name='NewNeuphonic')

print(result)
```

Alternatively, if you wanna provide the voice id:

```python
result = client.voices.update(voice_id=XXX)

print(result)
```


### Audio Generation

When generating audio, you can customize the process by setting various parameters in the **TTSConfig**. These parameters include options such as speed, voice, model, temperature, and more.

Both standard voices and your cloned voices are supported, and you can specify them using their respective voice IDs.

#### SSE (Server Side Events)
```python
from pyneuphonic import Neuphonic, TTSConfig
from pyneuphonic.player import AudioPlayer
import os

client = Neuphonic(api_key=os.environ.get('NEUPHONIC_API_TOKEN'))

sse = client.tts.SSEClient()

# TTSConfig is a pydantic model so check out the source code for all valid options, such as speed and voice
tts_config = TTSConfig(speed=1.05,  voice='ebf2c88e-e69d-4eeb-9b9b-9f3a648787a5')

# Create an audio player with `pyaudio`
with AudioPlayer() as player:
    response = sse.send('Hello, world!', tts_config=tts_config)
    player.play(response)

    player.save_audio('output.wav')  # save the audio to a .wav file
```

#### Asynchronous SSE
```python
from pyneuphonic import Neuphonic, TTSConfig
from pyneuphonic.player import AsyncAudioPlayer
import os
import asyncio

async def main():
    client = Neuphonic(api_key=os.environ.get('NEUPHONIC_API_TOKEN'))

    sse = client.tts.AsyncSSEClient()

    # Change the voice used for the audio by changing the ID below.
    tts_config = TTSConfig(speed=1.05, voice='ebf2c88e-e69d-4eeb-9b9b-9f3a648787a5')

    async with AsyncAudioPlayer() as player:
        response = sse.send('Hello, world!', tts_config=tts_config)
        await player.play(response)

        player.save_audio('output.wav')  # save the audio to a .wav file

asyncio.run(main())
```

#### Asynchronous Websocket
```python
from pyneuphonic import Neuphonic, TTSConfig, WebsocketEvents
from pyneuphonic.models import APIResponse, TTSResponse
from pyneuphonic.player import AsyncAudioPlayer
import os
import asyncio

async def main():
    client = Neuphonic(api_key=os.environ.get('NEUPHONIC_API_TOKEN'))

    ws = client.tts.AsyncWebsocketClient()

    # Change the voice used for the audio by changing the ID below.
    tts_config = TTSConfig(voice='ebf2c88e-e69d-4eeb-9b9b-9f3a648787a5')

    player = AsyncAudioPlayer()
    await player.open()

    # Attach event handlers. Check WebsocketEvents enum for all valid events.
    async def on_message(message: APIResponse[TTSResponse]):
        await player.play(message.data.audio)

    async def on_close():
        await player.close()

    ws.on(WebsocketEvents.MESSAGE, on_message)
    ws.on(WebsocketEvents.CLOSE, on_close)

    await ws.open(tts_config=tts_config)

    # A special symbol ' <STOP>' must be sent to the server, otherwise the server will wait for
    # more text to be sent before generating the last few snippets of audio
    await ws.send('Hello, world!', autocomplete=True)
    await ws.send('Hello, world! <STOP>')  # Both the above line, and this line, are equivalent

    await asyncio.sleep(3)  # let the audio play
    player.save_audio('output.wav')  # save the audio to a .wav file
    await ws.close()  # close the websocket and terminate the audio resources

asyncio.run(main())
```

### Saving Audio
As per the examples above, you can use the `AudioPlayer` object to save audio.
```python
player.save_audio('output.wav')
```
However, if you do not want to play audio and simply want to save it, check out the examples
in [snippets/sse/save_audio.py](./snippets/sse/save_audio.py) and
[snippets/websocket/save_audio.py](./snippets/websocket/save_audio.py) for examples on how to
do this.

### Agents
🚀 Exciting New Feature Alert! 🚀

Stay tuned for the upcoming release of our **Agents** feature! 🤖✨
With Agents, you'll be able to create, manage, and interact with intelligent virtual assistants like
never before.

🔜 **Coming Soon!** 🔜

## Example Applications
Check out the [snippets](./snippets/) folder for some example applications.
