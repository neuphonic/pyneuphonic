import pytest
import asyncio
from unittest.mock import AsyncMock, patch, call
from pyneuphonic.websocket import NeuphonicWebsocketClient
import base64
import datetime
import json


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
    client.on_close.assert_called_once()
    client.on_error.assert_not_called()
    client.play_audio.assert_called()


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
