import pytest
import asyncio
from unittest.mock import AsyncMock


@pytest.mark.asyncio
async def test_close(client):
    client._ws = AsyncMock()
    client._ws.close = AsyncMock()
    client._ws.open = True

    async def mock_listen_task():
        pass

    client._listen_task = asyncio.create_task(mock_listen_task())

    client.on_close = AsyncMock()
    client.teardown_pyaudio = AsyncMock()

    # Close the client
    await client.close()

    # Assert that the task was cancelled
    assert client._listen_task.cancelled()

    # other assertions
    client._ws.close.assert_called_once()
    client.on_close.assert_called_once()
    client.teardown_pyaudio.assert_called()
