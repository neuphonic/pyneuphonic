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

## Fun Examples
Set your API key in your environment through the terminal or in your `~/.zshrc` file.
```bash
export NEUPHONIC_API_TOKEN=XXXXX
```

The open a python shell in your terminal and do the following:
```python
import asyncio
from pyneuphonic.examples import speak
asyncio.run(speak('Hello, how are you?'))
```

Also, try this one:
```python
import asyncio
from pyneuphonic.examples import llama3_interactive
asyncio.run(llama3_interactive())
```
Note that the `llama3_interactive` example required that you have `ollama` installed and have downloaded the `llama3:8b`
model.

### Basic Usage
Everything that is important lives inside the `pyneuphonic.TTSStreamer` class.
The below script will convert "Hello, world!" to speech, and speak it aloud.
```python
from pyneuphonic import TTSStreamer
from pyneuphonic.utils import string_to_async_generator
import asyncio

text_generator = string_to_async_generator("Hello, world!")
tts = TTSStreamer(API_TOKEN='XXXXXX')

asyncio.run(asyncio.wait_for(tts.stream(text_generator), timeout=60))
```

Ensure to pass in your `API_TOKEN` as required, or instead set your `NEUPHONIC_API_TOKEN` environment variable and this
will be loaded automatically.

### Advanced Usage - Production Level
See [`pyneuphonic/examples/llama3_interactive`](pyneuphonic/examples/llama3_interactive.py) for an example on how to use
the `ollama` package with **llama3:8b**, alongside `TTSStreamer` to stream text-to-speech token-by-token (to make full
use of Neuphonic's low-latency TTS engine).

This is how the `TTSStreamer` should be used in practise.
