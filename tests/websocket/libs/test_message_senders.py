import pytest
from pyneuphonic.websocket import send_async_generator
from unittest.mock import AsyncMock, call


@pytest.mark.asyncio
async def test_string(client):
    client.send = AsyncMock()
    text = 'Hello, World! This is Neu.'

    await client.send(text)
    client.send.assert_called_once_with(text)


@pytest.mark.asyncio
async def test_send_async_generator(client):
    client.send = AsyncMock()

    async def text_generator():
        yield 'Hello, '
        yield 'World! '
        yield 'This '
        yield 'is '
        yield 'Neu.'

    await send_async_generator(client, text_generator())

    assert client.send.call_count == 6

    client.send.assert_has_calls(
        [call('Hello, '), call('World! '), call('This '), call('is '), call('Neu.')]
    )
