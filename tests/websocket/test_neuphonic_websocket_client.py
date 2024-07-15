import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from pyneuphonic.websocket import NeuphonicWebsocketClient
import datetime
import json
import base64


def test_instantiation(
    client,
    on_message,
    on_open,
    on_close,
    on_error,
    on_ping,
    on_pong,
    on_send,
):
    # Check the provided methods are bound
    assert client.on_message.__func__ == on_message
    assert client.on_open.__func__ == on_open
    assert client.on_close.__func__ == on_close
    assert client.on_error.__func__ == on_error
    assert client.on_ping.__func__ == on_ping
    assert client.on_pong.__func__ == on_pong
    assert client.on_send.__func__ == on_send

    # Check _bind_callbacks is called properly, which is sort of implicit in the above check
    with patch.object(NeuphonicWebsocketClient, '_bind_callbacks') as mock:
        client = NeuphonicWebsocketClient(
            NEUPHONIC_API_TOKEN='test_token',
            NEUPHONIC_WEBSOCKET_URL='wss://test_url',
            on_message=on_message,
            on_send=on_send,
        )

        mock.assert_called_once_with(on_message, None, None, None, None, None, on_send)


@pytest.mark.asyncio
async def test_create_ws_connection(client, unsecure_client):
    with patch('websockets.connect', new_callable=AsyncMock) as mock_connect:
        # assert the connection is created properly
        assert client._ws is None
        await client._create_ws_connection(ping_interval=20, ping_timeout=10)
        ssl_context = mock_connect.call_args.kwargs['ssl']
        mock_connect.assert_called_with(
            'wss://test_url/test_token',
            ssl=ssl_context,
            timeout=client._timeout,
            ping_interval=20,
            ping_timeout=10,
        )
        assert client._ws is not None

        assert unsecure_client._ws is None
        await unsecure_client._create_ws_connection(ping_interval=25, ping_timeout=15)
        mock_connect.assert_called_with(
            'ws://test_url/test_token',
            ssl=None,
            timeout=unsecure_client._timeout,
            ping_interval=25,
            ping_timeout=15,
        )
        assert unsecure_client._ws is not None


@pytest.mark.asyncio
async def test_listen(client):
    client._ws = AsyncMock()
    client._ws.open = True
    client._handle_message = AsyncMock()

    async def close_connection():
        await asyncio.sleep(0.1)
        client._ws.open = False

    with patch(
        'asyncio.create_task', side_effect=asyncio.create_task
    ) as mock_create_task:
        with patch('asyncio.wait', side_effect=asyncio.wait) as mock_wait:
            await asyncio.gather(client.listen(), close_connection())
            client._handle_message.assert_called()


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

    await client._handle_message()

    # Check that the correct handlers were called for each message
    client.on_message.assert_called_once_with(response)
    client.on_close.assert_called_once()
    client.on_error.assert_not_called()


@pytest.mark.asyncio
async def test_send(client):
    client._ws = AsyncMock()
    client.on_send = AsyncMock()

    message = 'test message'

    await client.send(message)

    client._ws.send.assert_called_once_with(message)
    client.on_send.assert_called_once_with(message)


@pytest.mark.asyncio
async def test_open(client):
    client._create_ws_connection = AsyncMock()
    client.on_open = AsyncMock()

    await client.open(ping_interval=20, ping_timeout=10)

    client._create_ws_connection.assert_called_with(20, 10)
    client.on_open.assert_called_once()


@pytest.mark.asyncio
async def test_close(client):
    client._ws = AsyncMock()
    client._ws.close = AsyncMock()
    client._ws.open = True
    client.on_close = AsyncMock()

    # Close the client
    await client.close()

    # Try to close the client when it is already closed
    client._ws.open = False
    await client.close()

    # assert that these were only called once, they weren't called the second time because the client is already closed
    client._ws.close.assert_called_once()
    client.on_close.assert_called_once()
