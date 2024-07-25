# Simple Text to Speech
The below example echo's back to the user, whatever the user inputs into the prompt.
We take the user's input, send it to the websocket, and then the audio is played back to the user using `pyaudio` by default.

`pip install pyaudio aioconsole` before running the example.

```{literalinclude} ../../../../snippets/simple_tts.py
:language: python
:caption: Echo Input Example
``
