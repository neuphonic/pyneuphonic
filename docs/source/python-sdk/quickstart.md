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
Here is a more verbose example of how to use the `NeuphonicWebsocketClient` and it's callback functionality.

```{literalinclude} ../../../snippets/basic_usage.py
:language: python
:caption: Verbose Example to Illustrate Callback Functionality
```

Notice that you will receive more than 1 audio messages even though you only sent 1 string.
This is because the audio is sent incrementally, word by word.

The `NeuphonicWebsocketClient` exposes the following callbacks:
- `on_message` - called after every response from the websocket,
- `on_open` -  called after websocket connection opens;
- `on_close` - called after the websocket connected closes;
- `on_error` - called to handle any exceptions;
- `on_send` - hooks into `NeuphonicWebsocketClient.send` and is called after every send;

See the [SDK Reference](sdk-reference.rst) for the complete API reference on the `NeuphonicWebsocketClient`.

## API Format
Messages to the websocket are sent as strings.
All responses from the websocket will be a dict with the following structure:

```{code-block} python
:caption: API Response Format
{
    'version': '1.X.X',
    'timestamp': '2024-07-15T11:59:27.619054',  # UTC server timestamp
    'data': {
        'audio': 'SGVsbG8h',  # base64 encoded audio byte string
        'text': 'Hello!'  # the text content of the audio data
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
Audio is produced incrementally, with a 1-word delay.
This means that
```python
client.send('Hello, how are ')
```
will not produce audio for the word "are " until the next word is sent with
```python
client.send('you ')
```
The server will always wait for the next word unless a message ends in one of: `['.', '!', '?']`, indicating the end of a
sentence.
This will trigger the server to produce audio for the last word.
So, in this case, to end the sentence you may send
```python
client.send('doing today?')
```
which will produce audio all the way to end of the sentence.
