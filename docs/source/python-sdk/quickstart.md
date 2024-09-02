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
export NEUPHONIC_WEBSOCKET_URL=wss://eu-west-1.api.neuphonic.com/speak/en
```

These are found and loaded by the client automatically.
Ensure to change the `NEUPHONIC_WEBSOCKET_URL` to point to the appropriate region.

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
See the [SDK Reference](sdk-reference.rst) for the complete API reference on the `NeuphonicWebsocketClient`.


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

#### Model Settings
See [WebSocket API - Authentication](../websocket-api.md#authentication) for a list of all model
settings which can be passed in as query parameters when connecting to the websocket.
Below is an example of how to change the audio playback speed.

```{literalinclude} ../../../snippets/playing_audio_speed.py
:language: python
:caption: Playing Audio Using PyAudio
```

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

As per the [WebSocket API - Sending Messages](../websocket-api.md#sending-messages) section, passages of text must
be terminated with the end-of-sequence token `<STOP>`. This can be done with either of the following:

```python
await client.send('Hello, World!', autocomplete=True)
```
```python
await client.send('Hello, World!')
await client.send('<STOP>')
```

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

### Timeout

The server will automatically disconnect any client that has been connected for longer than 90
seconds without sending any messages.
Below is an example of how to gracefully re-connect when this occurs.
```{literalinclude} ../../../snippets/class/timeout.py
:language: python
:caption: Handling Timeout
```
