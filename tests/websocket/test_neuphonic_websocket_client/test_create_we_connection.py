import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_create_ws_connection(client, unsecure_client):
    with patch('websockets.connect', new_callable=AsyncMock) as mock_connect:
        # assert the connection is created properly
        assert client._ws is None
        await client._create_ws_connection(ping_interval=20, ping_timeout=10)
        ssl_context = mock_connect.call_args.kwargs['ssl']
        mock_connect.assert_called_with(
            'wss://test_url',
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
            'ws://test_url',
            ssl=None,
            timeout=unsecure_client._timeout,
            ping_interval=25,
            ping_timeout=15,
            extra_headers={'x-api-key': 'test_token'},
        )
        assert unsecure_client._ws is not None
