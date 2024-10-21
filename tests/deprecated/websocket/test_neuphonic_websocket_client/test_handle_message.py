import pytest
from unittest.mock import AsyncMock
import base64
import datetime
import json


@pytest.mark.asyncio
async def test_handle_message(client):
    response = {
        'version': '1.0.0',
        'timestamp': datetime.datetime.now().isoformat(),
        'data': {
            'audio': base64.b64encode(b'Hello, ').decode('utf-8'),
            'text': 'Hello, ',
        },
    }

    # Mock the WebSocket connection
    client._ws = AsyncMock()
    client._ws.__aiter__.return_value = [json.dumps(response)]
    client._ws.open = True

    # Mock the message handlers
    client.on_message = AsyncMock()
    client.on_close = AsyncMock()
    client.on_error = AsyncMock()
    client.teardown_pyaudio = AsyncMock()
    client.play_audio = AsyncMock()

    await client._handle_message()

    # Check that the correct handlers were called for each message
    client.on_message.assert_called_once_with(response)
    client.on_error.assert_not_called()
    client.play_audio.assert_called()
