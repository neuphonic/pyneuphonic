# Quickstart

## Installation
Install this package into your environment using your chosen package manager:


```{code-block} bash
:caption: Pip
pip install git+ssh://git@github.com/neuphonic/pyneuphonic.git
```

```{code-block} bash
:caption: Poetry
poetry add git+ssh://git@github.com/neuphonic/pyneuphonic.git
```

## Set API Key
Set the following environment variables:
```{code-block} bash
export NEUPHONIC_API_TOKEN=[API KEY]
export NEUPHONIC_WEBSOCKET_URL=wss://neuphonic.us/speak/en
```

These are found and loaded by the client automatically.

## Basic Usage
The `PyNeuphonic` package exposes the `NeuphonicWebsocketClient` package and a variety of other helper functions.
Here is a simple example of how to use the `NeuphonicWebsocketClient` to send text and print out the length of the
audio received.

```{code-block} python
:caption: Basic Usage

import asyncio
from pyneuphonic.websocket import NeuphonicWebsocketClient
from base64 import b64decode

# Define callback functions
async def on_message(self: NeuphonicWebsocketClient, message: dict):
    audio_bytes = b64decode(message['data']['audio'])
    print(f"Received audio data: {len(audio_bytes)} bytes")

async def on_open(self: NeuphonicWebsocketClient):
    print("WebSocket connection opened")
    await client.send("Hello, Neuphonic!")

async def on_close(self: NeuphonicWebsocketClient):
    print("WebSocket connection closed")

# Create the client and pass in our callbacks
client = NeuphonicWebsocketClient(
    on_message=on_message,
    on_open=on_open,
    on_close=on_close
)

# Main function to run the client
async def main():
    await client.open()
    await client.listen()

# Run the client
asyncio.run(main())
```

The above example will connect to the websocket server, send the string "Hello, Neuphonic!, and log the length
of the returned audio bytes.
Notice that you will receive more than 1 audio message as our incremental TTS engine generates audio in smaller chunks.

The `NeuphonicWebsocketClient` exposes the following callbacks:
- `on_messae` - called after every response from the websocket,
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
    'timestamp': '2024-07-14T15:27:19.523584+00:00',
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
```{code-block} python
:caption: Playing Audio (Basic Example)

import asyncio
from pyneuphonic.websocket import NeuphonicWebsocketClient
from pyneuphonic.websocket.common.pyaudio import on_open, on_close, on_message
# from pyneuphonic.websocket.common.sounddevice import on_open, on_close, on_message

# Create the client
client = NeuphonicWebsocketClient(
    on_message=on_message,
    on_open=on_open,
    on_close=on_close
)

# Main function to run the client
async def main():
    await client.open()

    await asyncio.gather(
        client.listen(),
        client.send('Hello, World! My name is Neu.'),
    )

# Run the client
asyncio.run(main())
```

The imported `on_open, on_close` functions handle the set-up and tear-down of `pyaudio` resources,
and `on_message` handles streaming the received audio to the speaker.
You can switch between `pyaudio` and `sounddevice` by simply un-commenting the respective lines (lines 3 and 4, above).
To use the `sounddevice` implementations you need to install `numpy` and `sounddevice` first (`pip install numpy sounddevice`).
