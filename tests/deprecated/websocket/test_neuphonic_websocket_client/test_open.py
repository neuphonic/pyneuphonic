import pytest
import asyncio
from unittest.mock import AsyncMock, patch
import logging


@pytest.mark.asyncio
async def test_open(client):
    client._ws = AsyncMock()
    client._ws.open = True
    client._create_ws_connection = AsyncMock()
    client._handle_message = AsyncMock()
    client._listen = AsyncMock()

    async def close_connection():
        client._ws.open = False

    with patch(
        'asyncio.create_task', side_effect=asyncio.create_task
    ) as mock_create_task:
        with patch('asyncio.wait', side_effect=asyncio.wait) as mock_wait:
            await client.open(ping_interval=20, ping_timeout=10)
            await close_connection()
            client._create_ws_connection.assert_called_with(20, 10)
            client._listen.assert_called_once()


@pytest.mark.asyncio
async def test_server_close(client, caplog):
    """Ensure on_error is called when the open function fails."""
    client._ws = AsyncMock()
    client._ws.open = True
    client._create_ws_connection = AsyncMock()
    client._handle_message = AsyncMock()

    def raise_exception(*args, **kwargs):
        raise Exception('Test exception')

    client._listen = AsyncMock(side_effect=raise_exception)

    with caplog.at_level(logging.ERROR):
        await client.open(ping_interval=20, ping_timeout=10)

    assert 'Error opening WebSocket connection: Test exception' in caplog.text
    client._create_ws_connection.assert_called_with(20, 10)
    client._listen.assert_called_once()
