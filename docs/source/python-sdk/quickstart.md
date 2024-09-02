# Quickstart

## Installation
Install this package into your environment using your chosen package manager:


```{code-block} bash
:caption: Pip
pip install pyneuphonic
```

```{code-block} bash
:caption: Poetry
poetry add pyneuphonic
```

## Set API Key
Set the following environment variables:
```{code-block} bash
export NEUPHONIC_API_TOKEN=[API KEY]
export NEUPHONIC_WEBSOCKET_URL=wss://neuphonic.us/speak/en
```

These are found and loaded by the client automatically.

## Basic Usage

`pip install pyaudio` and then try the following code, the client will auto-detect `pyaudio` and use it to output incoming
audio.
```{literalinclude} ../../../snippets/playing_audio.py
:language: python
:caption: Playing Audio Using PyAudio
```
This snippet auto-detects `pyaudio` and uses it to play audio.

:::{note}
If `pyaudio` is **not** installed, and you run the above snippet no audio will be played.
:::

### NeuphonicWebsocketClient
The `PyNeuphonic` package exposes the `NeuphonicWebsocketClient` class and a variety of other helper functions.
This class can be inherited or used via callbacks.


#### Class-Based Implementation
Here is a **class-based** example of playing of how to play audio.
Note that this is roughly what `NeuphonicWebsocketClient` does under the hood when you set
`play_audio=True` with `pyaudio` is installed.
```{literalinclude} ../../../snippets/class/playing_audio_explicit.py
:language: python
:caption: Verbose Class-Based Example
```

#### Callback Implementation
Here is the exact same example as above, but in **callback** form.

```{literalinclude} ../../../snippets/callback/playing_audio_explicit.py
:language: python
:caption: Verbose Example to Illustrate Callback Functionality
```

#### Exposed Methods
The `NeuphonicWebsocketClient` exposes the following callbacks / methods that can be overriden:
- `on_message` - called after every response from the websocket,
- `on_open` -  called after websocket connection opens;
- `on_close` - called after the websocket connected closes;
- `on_error` - called to handle any exceptions;
- `on_send` - hooks into `NeuphonicWebsocketClient.send` and is called after every send;

See the [SDK Reference](sdk-reference.rst) for the complete API reference on the `NeuphonicWebsocketClient`.

## API Format
### Message Format
Messages to the websocket are sent as strings or dicts.
The websocket will accept either
```python
await client.send('Hello, World!')
```
or
```python
await client.send({'text': 'Hello, World!'})
```

Text can be sent in chunks of any arbitrary size, as demonstrated below:
```python
await client.send('Hel')
await client.send('lo, ')
await client.send('Wor')
await client.send('ld!')
```

All 3 examples above will produce the same audio output.

### Response Format

All responses from the websocket will be a dict with the following structure:

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

Audio is sent back to the user word by word.
To decode the audio back into bytes you would do the following:
```{code-block} python
:caption: Decoding Incoming Audio Data
import base64
base64.b64decode(response['data']['audio'])
```

### Terminating Sentences
Audio is produced incrementally.
This means that
```python
await client.send('Hello, how are ')
```
will return audio for only part of the above text.
Exactly how much audio is produced is slightly nuanced, but by rule of thumb it will generally
generate audio for everything except the last word.
If you send
```python
await client.send('you ')
```
then the server will continue to produce more audio.
To generate all of the audio up to the end of everything you have sent so far, you need to do
any one of the following 3.
```python
await client.send('doing today?', autocomplete=True)
```
```python
await client.send('doing today?')
await client.complete()
```
```python
await client.send('doing today?')
await client.send('<STOP>')
```
The `<STOP>` text is a special token which signals to the server that this is the end of a specific
segment of audio generation.

When should you send this token? This is dependent on your use case, for example, if you are
using an LLM to generate text, then you would send this token at the end of every response generation
from the LLM.
