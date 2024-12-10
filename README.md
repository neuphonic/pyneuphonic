# PyNeuphonic
The official Neuphonic Python library providing simple, convenient access to the Neuphonic text-to-speech websocket
API from any Python 3.9+ application.

For support or to get involved, join our [Discord](https://discord.gg/G258vva7gZ)!

- [PyNeuphonic](#pyneuphonic)
  - [Documentation](#documentation)
    - [Installation](#installation)
      - [API Key](#api-key)
    - [Voices](#voices)
      - [Get Voices](#get-voices)
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

#### API Key
Get your API key from the [Neuphonic website](https://beta.neuphonic.com) and set it in your
environment, for example:
```bash
export NEUPHONIC_API_TOKEN=<YOUR API KEY HERE>
```

### Voices
#### Get Voices
To get all available voices you can run the following snippet.
```python
from pyneuphonic import Neuphonic
import os

client = Neuphonic(api_key=os.environ.get('NEUPHONIC_API_TOKEN'))
voices = client.voices.get()  # get's all available voices

for voice in voices:
    print(voice)
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
#### SSE (Server Side Events)
```python
from pyneuphonic import Neuphonic, TTSConfig
from pyneuphonic.player import AudioPlayer
import os

client = Neuphonic(api_key=os.environ.get('NEUPHONIC_API_TOKEN'))

sse = client.tts.SSEClient()

# TTSConfig is a pydantic model so check out the source code for all valid options
tts_config = TTSConfig(
    model='neu_hq',
    speed=1.05,
    voice='e564ba7e-aa8d-46a2-96a8-8dffedade48f'  # use client.voices.get() to view all voice ids
)

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

    # Set the desired configurations: playback speed and voice
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

    # Set the desired voice
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

### Speech Restoration

Speech restoration involves enhancing and repairing degraded audio to improve its clarity, intelligibility, and overall quality, all while preserving the original content. Follow these simple steps to restore your audio clips:

#### Basic Restoration
To restore an audio clip without additional input, use the following code:

```python
voice_file_path = 'example.wav'
response = client.restorations.restore(voice_file_path)
```

#### Status of Restoration Job / Retrieve Results
Once you queue a job for restoration using the `.restore()` method you will receive an associated job id (uuid).
To get the status and the link to receive the results of your job you call the `.get()` method as following.

```python
client.restorations.get(job_id = job_id)
```



#### Restoration with a Transcript and Language Code
For better restoration quality, you can provide a transcript of the audio and specify a language code (default is English). Here's how:

```python
voice_file_path = 'example.wav'
transcript = 'Example Transcript' # Specify Transcript
lang_code = 'eng-us'  # Specify language code
is_transcript_file = False # Transcript is string
response = client.restorations.restore(voice_file_path, transcript, lang_code)
```

#### Restoration with a Transcript File
If you have the transcript stored in a file, you can use it instead of a transcript string:

```python
voice_file_path = 'example.wav'
transcript = 'example.txt'
lang_code = 'eng-us'
is_transcript_file = True # Switch this to true to feed in a file as transcript.
response = client.restorations.restore(voice_file_path, transcript, lang_code)
```
**NOTE:** You have to set is_transcript_file to true for the program to read this as a file rather than a string.


**Note:** Providing a transcript significantly improves the restoration quality of your audio clip. If no transcript is provided, the output may not be as refined.


### Agents

🚀 New Feature Alert! 🚀

With Agents, you'll be able to create, manage, and interact with intelligent AI assistants. You can create an agent
easily using the example here:

```python
import os
import asyncio

from pyneuphonic import Neuphonic, Agent, AgentConfig


async def main():
    client = Neuphonic(api_key=os.environ.get('NEUPHONIC_API_TOKEN'))

    agent_id = client.agents.create(
        name='Agent 1',
        prompt='You are a helpful agent. Answer in 10 words or less.',
        greeting='Hi, how can I help you today?'
    )['data']['id']

    agent = Agent(client, agent_id=agent_id, tts_model='neu_hq')

    await agent.start()

asyncio.run(main())
```

## Example Applications
Check out the [snippets](./snippets/) folder for some example applications.
