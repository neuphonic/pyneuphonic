# API Reference
The Neuphonic text-to-speech (TTS) API is composed primarily of two endpoints, serving a websocket
API and a server side events (SSE) API.
For the lowest latency, we recommend opting for the websocket API.

The API is located at:
 - Websocket: `wss://eu-west-1.api.neuphonic.com`
 - HTTP: `https://eu-west-1.api.neuphonic.com`

We deploy our servers as close to you as possible to give you the lowest latency.
Currently, we have deployments in `eu-west-1`, if you are unhappy with the latency in your region,
shoot us a message and we can get this resolved!

## Authentication
All requests to the TTS API must contain the `x-api-key` header or `api_key` query parameter to
authenticate your request.
```{code-block} python
:caption: Websocket authentication
import websockets

ws = await websockets.connect(
    'wss://eu-west-1.api.neuphonic.com/speak/en',
    extra_headers={'x-api-key': '<API_TOKEN>'},
)

await ws.send({'text': 'Hello, world!'})
```

```{code-block} python
:caption: SSE authentication
import httpx

with httpx.stream(
    method='POST',
    url='https://eu-west-1.api.neuphonic.com/sse/speak/en',
    headers={'x-api-key': '<API_TOKEN>'},
    json={'text': 'Hello, World!'},
) as response:
    for message in response.iter_lines():
        print(message)
```

## Voices
To retrieve a list of all available voices, use the `/voices` endpoint.
```{code-block} python
:caption: Websocket authentication
import httpx
import os

response = httpx.get(
    f'https://eu-west-1.api.neuphonic.com/voices',
    headers={'x-api-key': os.environ.get('NEUPHONIC_API_TOKEN')},
)

print(response.json())
```
Which will print a list of voices, with their corresponding `voice_id` and other metadata.

## Models
We currently have two models:
 - **neu_fast** - Our dynamic, incremental TTS model which generates audio with extremely low latency.
 - **neu_hq** - Our higher quality model which generates better sounding audio, at the cost of a
  small increase in latency.

```{code-block} python
:caption: Selecting the model (websocket)
import websockets

# Connect to the websocket with your desired parameters
ws = await websockets.connect(
    'wss://eu-west-1.api.neuphonic.com/speak/en?model=<MODEL>&voice=<VOICE_ID>"&...',
    extra_headers={'x-api-key': '<API_TOKEN>'},
)

await ws.send({'text': 'Hello, world!'})
```

```{code-block} python
:caption: Selecting the model (SSE)
import httpx

# Connect to the SSE with your desired parameters
with httpx.stream(
    method='POST',
    url='https://eu-west-1.api.neuphonic.com/sse/speak/en',
    headers={'x-api-key': '<API_TOKEN>'},
    json={'text': 'Hello, World!', model: {model: '<MODEL>', voice: '<VOICE_ID>'}},
) as response:
    for message in response.iter_lines():
        print(message)
```

### Options
There are a variety of options that you can pass into the models to alter the audio output.
These are all passed into the websocket as query parameters or in the body of the SSE request.
 - `model` - one of `neu_fast` or `neu_hq`.
 - `voice` - this is the `voice_id` for your desired voice.
 - `speed` - the audio playback speed. Can range from 0.7 to 1.6.
 - `temperature` - this is the randomness you want to introduce into the audio generation. Default
 is 0.5 and this must be between 0 and 1. This is only valid for the `neu_fast` model.
 - `sampling_rate` - this is the sampling rate of the returned audio. Default is 22050 and this must
 be either 22050 and 8000.
 - `encoding` - the encoding of the returned audio. Defaut is `pcm_linear` and this must be either
 `pcm_linear` or `pcm_mulaw` (the latter of which you would use if you were generating audio to be
 played on a phone call).
 - `language_id` - this is set at the end of the url `/speak/{language_id}` or `/sse/speak/{language_id}`
 and dictates the language used for the input text and output audio. We currently only offer english
 so this must be set to `en`.


## Playing Audio and SDKs
We recommend checking out our [Python SDK](https://github.com/neuphonic/pyneuphonic) which simplifies a lot of the above and provides an
easy way to interact, generate and play audio with the Neuphonic API.

Reach out to us at support@neuphonic.com you would like an SDK for another language or framework, or
join our [Discord](https://discord.gg/G258vva7gZ).
