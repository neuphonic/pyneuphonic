# Forwarding Audio
Another common use case is forwarding audio to a separate device for playback.
In this scenario, the Neuphonic SDK client runs on your server and forwards the audio to a third-party device where it's actually played.
The example below builds on the [Simple Text to Speech](./simple-tts.md) example, adding the ability to forward audio to a remote playback device.

`pip install aioconsole` before running the example.

```{literalinclude} ../../../../snippets/forwarding_audio.py
:language: python
:caption: Realtime Forwarding Audio Example
``
