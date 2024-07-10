# pyneuphonic
Python SDK for the Neuphonic TTS engine.

## Getting Started
This repository is an early implementation of the Neuphonic python SDK to interact with the websocket API for text to
speech functionality.

### Installation
Install this package into your environment using your chosen package manager:

**pip**:
```bash
pip install git+ssh://git@github.com/neuphonic/pyneuphonic.git
```
**poetry**
```bash
poetry add git+ssh://git@github.com/neuphonic/pyneuphonic.git
```

### Set API Key
Set the following environment variables:
```bash
export NEUPHONIC_API_TOKEN=XXX
export NEUPHONIC_WEBSOCKET_URL=wss://neuphonic.us/speak/en
```

### Interactive Example
See [`pyneuphonic/snippets/`](snippets) for some examples on mini-programs.
Run the `speak` example, which launches an interactive terminal where anything you type will be converted to text and
spoken back to you.

Open a python terminal and run the following:

```bash
from pyneuphonic.snippets import speak
import asyncio

asyncio.run(speak())
```

## Basic Usage

Here is a simple example of how to use the `NeuphonicWebsocketClient`.

```python
import asyncio
from pyneuphonic.websocket import NeuphonicWebsocketClient

# Define callback functions
async def on_audio_message(client, message):
    print(f"Received audio data: {len(message)} bytes")

async def on_non_audio_message(client, message):
    print(f"Received non-audio message: {message}")

async def on_open(client):
    print("WebSocket connection opened")
    await client.send("Hello, Neuphonic!")

async def on_close(client):
    print("WebSocket connection closed")

# Create the client
client = NeuphonicWebsocketClient(
    on_audio_message=on_audio_message,
    on_non_audio_message=on_non_audio_message,
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

The `NeuphonicWebsocketClient` exposes the following callbacks:
- `on_audio_message` - called after audio data (bytes) are received;
- `on_non_audio_message` - called after any other non-audio message is received;
- `on_open` -  called after websocket connection opens;
- `on_close` - called after the websocket connected closes;
- `on_error` - called to handle any exceptions;
- `on_send` - hooks into `NeuphonicWebsocketClient.send` and is called after every send;
- `on_ping` - called on every ping;
- `on_pong` - called on every pong;

Which can all be passed into the `NeuphonicWebsocketClient` constructor, as per the above example.
Alternatively, you can inherit the `NeuphonicWebsocketClient` class for maximal flexibility.

### Playing Audio
There is maximal flexibility for you to use the `NeuphonicWebsocketClient` to play audio however you want via the callbacks.
Default `PyAudio` and `sounddevice` implementations have been provided in [`pyneuphonic/websocket/common`](pyneuphonic/websocket/common),
both of these packages are python wrappers for [PortAudio](https://www.portaudio.com/); these are available to use or
implement yourself.

Here is an example on how to use `PyAudio` to automatically play any received audio through your speaker.
```python
import asyncio
from pyneuphonic.websocket import NeuphonicWebsocketClient
from pyneuphonic.websocket.common.pyaudio import on_open, on_close, on_audio_message
# from pyneuphonic.websocket.common.sounddevice import on_open, on_close, on_audio_message

# Create the client
client = NeuphonicWebsocketClient(
    on_audio_message=on_audio_message,
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

The imported `on_open, on_close` functions handle the set-up and tear-down of `PyAudio` resources,
and `on_audio_message` handles streaming the received audio to the speaker.
You can switch between `PyAudio` and `sounddevice` by simply un-commenting the respective lines (lines 3 and 4, above).

### Documentation
See XXX for full documentation.
