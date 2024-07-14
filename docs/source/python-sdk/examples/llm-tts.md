# LLM Output Streaming
A great use case for our incremental TTS engine is streaming output text tokens from LLMs directly into our websocket
for low-latency audio output. The snippet below gives an example of how to use `PyNeuphponic` to create a terminal
chatbot with llama3:8b.

This example demonstrates how to stream output from an LLM token by token and make effective use of the low-latency
incremental TTS engine.

```{literalinclude} ../../../../snippets/llama3_interactive.py
:language: python
``
