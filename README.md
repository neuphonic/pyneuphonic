# PyNeuphonic
The official Neuphonic Python library providing simple, convenient access to the Neuphonic text-to-speech websocket
API from any Python 3.9+ application.

For comprehensive guides and official documentation, check out [https://docs.neuphonic.com](https://docs.neuphonic.com).
If you need support or want to join the community, visit our [Discord](https://discord.gg/G258vva7gZ)!


- [PyNeuphonic](#pyneuphonic)
  - [Documentation](#documentation)
    - [Installation](#installation)
      - [API Key](#api-key)
    - [Voices](#voices)
      - [Get Voices](#get-voices)
      - [Get Voice](#get-voice)
      - [Clone Voice](#clone-voice)
      - [Update Voice](#update-voice)
      - [Delete Voice](#delete-voice)
    - [Audio Generation](#audio-generation)
      - [Configure the Text-to-Speech Synthesis](#configure-the-text-to-speech-synthesis)
      - [SSE (Server Side Events)](#sse-server-side-events)
      - [Asynchronous SSE](#asynchronous-sse)
      - [Asynchronous Websocket](#asynchronous-websocket)
    - [Saving Audio](#saving-audio)
    - [Speech Restoration](#speech-restoration)
      - [Basic Restoration](#basic-restoration)
      - [Get Status of Restoration Job / Retrieve Results](#get-status-of-restoration-job--retrieve-results)
      - [List all Active and Historic Jobs](#list-all-active-and-historic-jobs)
      - [Restoration with a Transcript and Language Code](#restoration-with-a-transcript-and-language-code)
      - [Restoration with a Transcript File](#restoration-with-a-transcript-file)
    - [Agents](#agents)
      - [List agents](#list-agents)
      - [Get agent](#get-agent)
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
export NEUPHONIC_API_KEY=<YOUR API KEY HERE>
```

### Voices
#### Get Voices
To get all available voices you can run the following snippet.
```python
from pyneuphonic import Neuphonic
import os

client = Neuphonic(api_key=os.environ.get('NEUPHONIC_API_KEY'))
response = client.voices.list()  # get's all available voices
voices = response.data['voices']

voices
```

#### Get Voice
To get information about an existing voice please call.
```python
response = client.voices.get(voice_id='<VOICE_ID>')  # gets information about the selected voice id
response.data  # response contains all information about this voice
```


#### Clone Voice

To clone a voice based on a audio file, you can run the following snippet.

```python
from pyneuphonic import Neuphonic
import os

client = Neuphonic(api_key=os.environ.get('NEUPHONIC_API_KEY'))

response = client.voices.clone(
    voice_name='<VOICE_NAME>',
    voice_tags=['tag1', 'tag2'],  # optional, add descriptive tags of what your voice sounds like
    voice_file_path='<FILE_PATH>.wav'  # replace with file path to a sample of the voice to clone
)

response.data  # this will contain a success message with the voice_id of the cloned voice
```

If you have successfully cloned a voice, the following message will be displayed: "Voice has
successfully been cloned with ID `<VOICE_ID>`." Once cloned, you can use this voice just like any of
the standard voices when calling the TTS (Text-to-Speech) service.

To see a list of all available voices, including cloned ones, use `client.voices.list()`.

**Note:** Your voice reference clip must meet the following criteria: it should be at least 6
seconds long, in .mp3 or .wav format, and no larger than 10 MB in size.

#### Update Voice

You can update any of the attributes of a voice: name, tags and the reference audio file the voice
was cloned on.
You can select which voice to update using either it's `voice_id` or it's name.

```python
# Updating using the original voice's name
response = client.voices.update(
    voice_name='<ORIGINAL_VOICE_NAME>',  # this is the name of voice we want to update

    # Provide any, or all of the following, to update the voice
    new_voice_name='<NEW_VOICE_NAME>',
    new_voice_tags=['new_tag_1', 'new_tag_2'],  # overwrite all previous tags
    new_voice_file_path='<NEW_FILE_PATH>.wav',
)

response.data
```

```python
# Updating using the original voice's `voice_id`
response = client.voices.update(
    voice_id ='<VOICE_ID>',  # this is the id of voice we want to update

    # Provide any, or all of the following, to update the voice
    new_voice_name='<NEW_VOICE_NAME>',
    new_voice_tags=['new_tag_1', 'new_tag_2'],  # overwrite all previous tags
    new_voice_file_path='<NEW_FILE_PATH>.wav',
)

response.data
```

**Note:** Your voice reference clip must meet the following criteria: it should be at least 6 seconds long, in .mp3 or .wav format, and no larger than 10 MB in size.

#### Delete Voice
To delete a cloned voice:

```python
# Delete using the voice's name
response = client.voices.delete(voice_name='<VOICE_NAME>')
response.data
```
```python
# Delete using the voices `voice_id`
response = client.voices.delete(voice_id='<VOICE_ID>')
response.data
```

### Audio Generation

#### Configure the Text-to-Speech Synthesis
To configure the TTS settings, modify the TTSConfig model.
The following parameters are examples of parameters which can be adjusted. Ensure that the selected combination of model, language, and voice is valid. For details on supported combinations, refer to the [Models](https://docs.neuphonic.com/resources/models) and [Voices](https://docs.neuphonic.com/resources/voices) pages.

- **`model`**
  The text-to-speech model to use.

  **Default**: `'neu_fast'`
  **Examples**: `'neu_fast'`, `'neu_hq'`

- **`lang_code`**
  Language code for the desired language.

  **Default**: `'en'` **Examples**: `'en'`, `'es'`, `'de'`, `'nl'`

- **`voice`**
  The voice ID for the desired voice. Ensure this voice ID is available for the selected model and language.

  **Default**: `None` **Examples**: `'8e9c4bc8-3979-48ab-8626-df53befc2090'`

- **`speed`**
  Playback speed of the audio.

  **Default**: `1.0`
  **Examples**: `0.7`, `1.0`, `1.5`

View the [TTSConfig](https://github.com/neuphonic/pyneuphonic/blob/main/pyneuphonic/models.py) object to see all valid options.

#### SSE (Server Side Events)
```python
from pyneuphonic import Neuphonic, TTSConfig
from pyneuphonic.player import AudioPlayer
import os

client = Neuphonic(api_key=os.environ.get('NEUPHONIC_API_KEY'))

sse = client.tts.SSEClient()

# View the TTSConfig object to see all valid options
tts_config = TTSConfig(
    model='neu_hq',
    speed=1.05,
    lang_code='en',
    voice_id='e564ba7e-aa8d-46a2-96a8-8dffedade48f'  # use client.voices.list() to view all voice ids
)

# Create an audio player with `pyaudio`
with AudioPlayer() as player:
    response = sse.send('Hello, world!', tts_config=tts_config)
    player.play(response)

    player.save_audio('output.wav')  # save the audio to a .wav file from the player
```

#### Asynchronous SSE
```python
from pyneuphonic import Neuphonic, TTSConfig
from pyneuphonic.player import AsyncAudioPlayer
import os
import asyncio

async def main():
    client = Neuphonic(api_key=os.environ.get('NEUPHONIC_API_KEY'))

    sse = client.tts.AsyncSSEClient()

    # Set the desired configurations: playback speed and voice
    tts_config = TTSConfig(speed=1.05, lang_code='en', voice_id='ebf2c88e-e69d-4eeb-9b9b-9f3a648787a5')

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
    client = Neuphonic(api_key=os.environ.get('NEUPHONIC_API_KEY'))

    ws = client.tts.AsyncWebsocketClient()

    # Set the desired voice
    tts_config = TTSConfig(voice_id='ebf2c88e-e69d-4eeb-9b9b-9f3a648787a5')

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
To save the audio to a file, you can use the `save_audio` function from the `pyneuphonic` package to save the audio from responses from the synchronous SSE client.

```python
from pyneuphonic import save_audio

...
response = sse.send('Hello, world!', tts_config=tts_config)

save_audio(response, 'output.wav')
```

The `save_audio` function takes in two arguments: the response from the TTS service (as well as audio bytes) and the file path to save the audio to.

For async responses, you can use the `async_save_audio` function.

```python
from pyneuphonic.player import async_save_audio

...

response = sse.send('Hello, world!', tts_config=tts_config)

await async_save_audio(response, 'output.wav')
```

### Speech Restoration

Speech restoration involves enhancing and repairing degraded audio to improve its clarity, intelligibility, and overall quality, all while preserving the original content. Follow these simple steps to restore your audio clips:

**Note:** Your audio clip must meet the following criteria: it should be in .mp3 or .wav format, and no larger than 10 MB in size.

#### Basic Restoration
To restore an audio clip without additional input, use the following code:

```python
# Submit a request to restore a degraded file
voice_file_path = '<FILE_PATH>.wav'  # select a degraded file to restore
restoration_response = client.restorations.restore(voice_file_path)
print(restoration_response.data)  # a dictionary containing the job_id

# Get the status of the job
job_id = restoration_response.data['job_id']
status_response = client.restorations.get(job_id=job_id)
print(status_response.data)
```
If the job is completed, the status will include the URL where you can access the results (file_url). If the status is 'Not Finished,' please wait a moment before rerunning restorations.get(). Once the status changes to 'Finished,' you will be able to retrieve the results.

#### Get Status of Restoration Job / Retrieve Results
Once you queue a job for restoration using the `.restore()` method you will receive an associated job id (uuid) as a member of the response.
To get the status and the link to receive the results of your job you call the `.get()` method as following.

```python
response = client.restorations.get(job_id='<JOB_ID>')
response.data  # a dict with the status of the job and the url where you can download the results.
```

#### List all Active and Historic Jobs
To list all your active and previous jobs you can run the `.jobs()` function.
```python
response = client.restorations.list()
response.data
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
response = client.restorations.restore(voice_file_path, transcript, lang_code, is_transcript_file=True)
```
**Note:** You have to set is_transcript_file to true for the program to read this as a file rather than a string.

**Note:** Providing a transcript significantly improves the restoration quality of your audio clip. If no transcript is provided, the output may not be as refined.


### Agents
With Agents, you can create, manage, and interact with intelligent AI assistants. You can create an
agent easily using the example here:
```python
import os
import asyncio

# View the AgentConfig object for a full list of parameters to configure the agent
from pyneuphonic import Neuphonic, Agent, AgentConfig


async def main():
    client = Neuphonic(api_key=os.environ.get('NEUPHONIC_API_KEY'))

    agent_id = client.agents.create(
        name='Agent 1',
        prompt='You are a helpful agent. Answer in 10 words or less.',
        greeting='Hi, how can I help you today?'
    ).data['agent_id']

    # All additional keyword arguments (such as `agent_id` and `tts_model`) are passed as
    # parameters to the model. See AgentConfig model for full list of parameters.
    agent = Agent(client, agent_id=agent_id, tts_model='neu_hq')

    try:
        await agent.start()

        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await agent.stop()

asyncio.run(main())
```

#### List agents
To list all your agents:
```python
response = client.agents.list()
response.data
```

#### Get agent
To get information about a specific agent:
```python
response = client.agents.get(agent_id='<AGENT_ID>')
response.data
```


## Example Applications
Check out the [examples](./examples/) folder for some example applications.
