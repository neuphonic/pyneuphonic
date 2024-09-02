import pytest
from unittest.mock import AsyncMock, call


@pytest.mark.asyncio
async def test_send(client):
    client.send = AsyncMock(side_effect=client.send)
    client._ws = AsyncMock()
    client.on_send = AsyncMock(side_effect=client.on_send)
    client.complete = AsyncMock(side_effect=client.complete)

    message = 'test message'

    await client.send(message, autocomplete=True)

    assert client._ws.send.call_count == 2
    client._ws.send.assert_has_calls(
        [call('test message'), call('{"text": " <STOP>"}')]
    )

    client.on_send.call_count == 2
    client.on_send.assert_has_calls([call('test message'), call({'text': ' <STOP>'})])

    client.complete.assert_called_once()
