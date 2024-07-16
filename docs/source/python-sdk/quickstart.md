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
The `PyNeuphonic` package exposes the `NeuphonicWebsocketClient` class and a variety of other helper functions.
Here is a simple example of how to use the `NeuphonicWebsocketClient` to send text and print out the length of the
audio received.

```{literalinclude} ../../../snippets/basic_usage.py
:language: python
:caption: Basic Usage
```

The above example will connect to the websocket server, send the string "Hello, Neuphonic!, and log the length
of the returned audio bytes.
Notice that you will receive more than 1 audio message as our incremental TTS engine generates audio in smaller chunks.

The `NeuphonicWebsocketClient` exposes the following callbacks:
- `on_message` - called after every response from the websocket,
- `on_open` -  called after websocket connection opens;
- `on_close` - called after the websocket connected closes;
- `on_error` - called to handle any exceptions;
- `on_send` - hooks into `NeuphonicWebsocketClient.send` and is called after every send;

Which can all be passed into the `NeuphonicWebsocketClient` constructor, as per the above example.
Alternatively, you can inherit the `NeuphonicWebsocketClient` class to override these methods, it is entirely up to your
own coding style.

### API Response Format
All responses from the websocket will look like this:

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

Generally, audio is sent back to the user word by word.
To decode the audio back into bytes you would do the following:
```{code-block} python
:caption: Decoding Incoming Audio Data
import base64
base64.b64decode(response['data']['audio'])
```

### Playing Audio
There is maximal flexibility for you to use the `NeuphonicWebsocketClient` to play audio however you want via the callbacks.
Two popular python packages to play audio are `pyaudio` and `sounddevice`, and so implementations to play audio with these
packages have been provided.

Both of these packages are wrappers for [PortAudio](https://www.portaudio.com/), therefore PortAudio needs to be installed
and configured on your system.

Below is an example on how to use `pyaudio` to play the string "Hello, World! My name is Neu." out of your speaker.

First install `pyaudio` (`pip install pyaudio`) and then try the following code:
```{literalinclude} ../../../snippets/playing_audio.py
:language: python
:caption: Playing Audio (Basic Example)
```

What is happening here?
1. We import the provided `pyaudio` callback implementations
   - `on_open` will set up audio resources when the websocket connection is made.
   - `on_message` will handle incoming messages and pass them to the audio resources to play.
   - `on_close` will tear down audio resources when the client is disconnected.
2. We pass these callbacks into the `client` when instantiating it.
3. In the main function we open the connection, start listening for incoming messages and then send a message.
We close the connection, and `client.close` will, by default, wait for all audio to be received before closing the connection.
You can force close the connection by doing `client.close(force=True)` with no guarantee that all audio will have been
received at this point in time.

You can switch between `pyaudio` and `sounddevice` by simply un-commenting the respective lines (lines 3 and 4, above).
To use the `sounddevice` implementations you need to install `numpy` and `sounddevice` first (`pip install numpy sounddevice`).
