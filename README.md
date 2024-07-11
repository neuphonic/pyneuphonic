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

The above example will connect to the websocket server, send the string "Hello, Neuphonic!, and log the length
of the returned audio bytes.
Notice that you will receive more than 1 audio message as our incremental TTS engine generates audio in smaller chunks.

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
Alternatively, you can inherit the `NeuphonicWebsocketClient` class to override these methods, it is entirely up to your
own coding style.

### Playing Audio
There is maximal flexibility for you to use the `NeuphonicWebsocketClient` to play audio however you want via the callbacks.
Two popular python packages to play audio are `pyaudio` and `sounddevice`, and so implementations to play audio through
your system's speaker with these packages have been provided.
Both of these packages are wrappers for [PortAudio](https://www.portaudio.com/) and so PortAudio needs to be installed and configured on your system.
These implementations have been provided in [`pyneuphonic/websocket/common`](pyneuphonic/websocket/common).

Below is an example on how to use `pyaudio` to play the string "Hello, World! My name is Neu." out of your speaker.

First install `pyaudio` (`pip install poetry`) and then try the following code:
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

The imported `on_open, on_close` functions handle the set-up and tear-down of `pyaudio` resources,
and `on_audio_message` handles streaming the received audio to the speaker.
You can switch between `pyaudio` and `sounddevice` by simply un-commenting the respective lines (lines 3 and 4, above).
To use the `sounddevice` implementations you need to install `numpy` and `sounddevice` first (`pip install numpy sounddevice`).

### Token-by-token LLM to TTS Streaming
See [`snippets/`](snippets) for some examples on mini-programs.
A great use case for our incremental TTS engine is streaming output text tokens from LLMs directly into our websocket
for low-latency audio output.
To see an example of how to use **llama3:8b** check out the [`snippets/llama3_interactive.py`](snippets/llama3_interactive.py)
script (you will need to `pip install ollama aioconsole` and install [llama3:8b](https://ollama.com/library/llama3:8b)).

For another example, see the [`snippets/speak.py`](snippets/speak.py), which launches an interactive terminal where anything you type will be converted to text and
spoken back to you (this example requires `pip install aioconsole`).


## Documentation
See XXX for full documentation.
