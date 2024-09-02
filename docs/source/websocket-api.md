# Websocket API
The websocket API allows you to stream text to our server, and our server's will stream audio
chunks back to you in base64 encoded format.

## Authentication
To create a connection and authenticate, you will need to connect to the appropriately located
server and pass your API key in the `x-api-key` header.
```{code-block} python
:caption: Authentication (Python Example)
import websockets
import ssl

ws = await websockets.connect(
    'wss://eu-west-1.api.neuphonic.com/speak/en',
    ssl=ssl.create_default_context(cafile=certifi.where()),
    extra_headers={'x-api-key': '<API_TOKEN>'},
)
```
Note the syntax for our websocket endpoints is `wss://{aws_region}.api.neuphonic.com/speak/{language_id}`.

:::{note}
Connect to the region closest to you for the lowest latency. Contact us if your region is unavailable.
:::

## Sending Messages
Messages can be sent to the server either word by word, sentence by sentence, or however is appropriate
for your use case.
```{code-block} python
:caption: Sending Messages (Python Example 1)
await ws.send({'text': 'Hello, '})
await ws.send({'text': 'World!'})
await ws.send({'text': '<STOP>'})
```

```{code-block} python
:caption: Sending Messages (Python Example 2)
await ws.send({'text': 'Hello, World!<STOP>'})
```
We require a special end-of-sequence token `<STOP>` to be sent at the end of every passage of audio
to ensure that the server returns all the audio chunks up to that point. This may be
 - at the end of every sentence;
 - after your LLM has generated a passage of text;
 - just before you request user input;

Our dynamic incremental TTS generates audio with a small lookahead, so it requires the `<STOP>` to
indicate that there is no more text, and it should generate the last snippet of audio.

## Response Format
All responses from the server be JSON and look like this:
```{code-block} python
:caption: API Response Format
{
    'version': '1.X.X',
    'timestamp': '2024-07-15T11:59:27.619054',  # UTC server timestamp
    'data': {
        'audio': 'SGVsbG8h',  # base64 encoded audio byte string
    }
}
```
Responses will be incrementally sent from the server to the client, so each response will contain
audio for a small segment (roughly 1 word) of the text sent to the server.
This is irregardless of whether text was sent as a sentence or word by word, the client will always
receive audio in small chunks.

Audio can be decoded using
```{code-block} python
:caption: Decoding Audio
import base64
audio_bytes = base64.b64decode(message['data']['audio'])
```

The audio returned is mono (single-channel) with a **sample rate** of 44.1 kHz and a (signed) 16-bit **depth**.