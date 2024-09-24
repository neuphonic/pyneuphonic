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
export NEUPHONIC_API_URL=eu-west-1.api.neuphonic.com
```

These are found and loaded by the client automatically.
Ensure to change the `NEUPHONIC_API_URL` to point to the appropriate region.

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
Here is a **class-based inheritance** example of playing of how to play audio.
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

Both implementations work perfectly fine, choose whichever works best for your use case!

#### Exposed Methods
The `NeuphonicWebsocketClient` exposes the following callbacks / methods that can be overriden or passed in during initialization:
- `on_message` - called after receiving each response from the websocket
- `on_error` - invoked to handle any exceptions that occur
- `on_open` - triggered when the websocket connection is established, following a call to `NeuphonicWebsocketClient.open`
- `on_close` - executed when the websocket connection terminates, after calling `NeuphonicWebsocketClient.close`
- `on_send` - called after each message is sent via `NeuphonicWebsocketClient.send`

#### Model Settings
See [WebSocket API - Authentication](../websocket-api.md#authentication) for a list of all model
settings which can be passed in when connecting to the websocket.
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

For details on the API response structure, including audio data format and decoding,
see [WebSocket API - Response Format](../websocket-api.md#response-format).
Responses are JSON objects containing the base64-encoded audio chunks.

### Timeout

The server will automatically disconnect any client that has been connected for longer than 90
seconds without sending any messages.
Below is an example of how to gracefully re-connect when this occurs, in case longer lasting connections
are required.
```{literalinclude} ../../../snippets/class/timeout.py
:language: python
:caption: Handling Timeout
```
