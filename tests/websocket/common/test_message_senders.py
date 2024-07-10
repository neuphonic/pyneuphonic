import pytest
from pyneuphonic.websocket.common.message_senders import (
    send_async_generator,
    send_string,
)
from unittest.mock import AsyncMock, call


@pytest.mark.asyncio
async def test_string(client):
    client.send = AsyncMock()
    text = 'Hello, World! This is Neu.'

    await send_string(client, text)

    assert client.send.call_count == 5

    client.send.assert_has_calls(
        [call('Hello, '), call('World! '), call('This '), call('is '), call('Neu.')]
    )


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

    assert client.send.call_count == 5

    client.send.assert_has_calls(
        [call('Hello, '), call('World! '), call('This '), call('is '), call('Neu.')]
    )
