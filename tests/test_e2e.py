import pytest
from pyneuphonic.models import (
    SSEResponse,
    WebsocketResponse,
    WebsocketEvents,
    VoiceItem,
)
import asyncio


def test_sse_sync(client):
    sse_client = client.tts.SSEClient()

    response = sse_client.send('This is a test.')

    count = 0

    for item in response:
        count += 1
        assert isinstance(item, SSEResponse)

    assert count > 0


@pytest.mark.asyncio
async def test_sse_async(client):
    sse_client = client.tts.AsyncSSEClient()

    response = sse_client.send('This is a test.')

    count = 0

    async for item in response:
        count += 1
        assert isinstance(item, SSEResponse)

    assert count > 0


@pytest.mark.asyncio
async def test_websocket_async(client):
    ws = client.tts.AsyncWebsocketClient()

    on_open_called = False
    message_count = 0
    on_error_called = False
    on_close_called = False

    async def on_open():
        nonlocal on_open_called
        on_open_called = True

    async def on_message(message: WebsocketResponse):
        nonlocal message_count
        message_count += 1

        assert isinstance(message, WebsocketResponse)

    async def on_close():
        nonlocal on_close_called
        on_close_called = True

    async def on_error(e: Exception):
        nonlocal on_error_called
        on_error_called = True

    ws.on(WebsocketEvents.OPEN, on_open)
    ws.on(WebsocketEvents.MESSAGE, on_message)
    ws.on(WebsocketEvents.ERROR, on_error)
    ws.on(WebsocketEvents.CLOSE, on_close)

    await ws.open()
    await asyncio.sleep(0.5)

    await ws.send('This is a test.', autocomplete=True)
    await asyncio.sleep(1)
    await ws.close()
    await asyncio.sleep(0.5)

    assert on_open_called is True
    assert message_count > 0
    assert on_error_called is False
    assert on_close_called is True


def test_get_voices(client):
    voices = client.voices.get()

    assert len(voices) > 0

    for voice in voices:
        assert isinstance(voice, VoiceItem)
