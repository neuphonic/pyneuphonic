import pytest
from unittest.mock import AsyncMock, patch
from pyneuphonic.websocket import NeuphonicWebsocketClient


@pytest.mark.asyncio
async def test_create_ws_connection(client, unsecure_client):
    with patch('websockets.connect', new_callable=AsyncMock) as mock_connect:
        # assert the connection is created properly
        assert client._ws is None
        await client._create_ws_connection(ping_interval=20, ping_timeout=10)
        ssl_context = mock_connect.call_args.kwargs['ssl']
        mock_connect.assert_called_with(
            'wss://eu-west-1.api.test.com/speak/en',
            ssl=ssl_context,
            timeout=client._timeout,
            ping_interval=20,
            ping_timeout=10,
            extra_headers={'x-api-key': 'test_token'},
        )
        assert client._ws is not None

        assert unsecure_client._ws is None
        await unsecure_client._create_ws_connection(ping_interval=25, ping_timeout=15)
        mock_connect.assert_called_with(
            'ws://localhost:8080/speak/en',
            ssl=None,
            timeout=unsecure_client._timeout,
            ping_interval=25,
            ping_timeout=15,
            extra_headers={'x-api-key': 'test_token'},
        )
        assert unsecure_client._ws is not None


@pytest.mark.asyncio
async def test_query_params():
    client = NeuphonicWebsocketClient(
        NEUPHONIC_API_TOKEN='test_token',
        NEUPHONIC_API_URL='eu-west-1.api.test.com',
        params={'temperature': 1.0, 'speed': 1.2},
    )

    with patch('websockets.connect', new_callable=AsyncMock) as mock_connect:
        await client._create_ws_connection(ping_interval=20, ping_timeout=10)
        ssl_context = mock_connect.call_args.kwargs['ssl']

        mock_connect.assert_called_with(
            'wss://eu-west-1.api.test.com/speak/en?temperature=1.0&speed=1.2',
            ssl=ssl_context,
            timeout=client._timeout,
            ping_interval=20,
            ping_timeout=10,
            extra_headers={'x-api-key': 'test_token'},
        )
