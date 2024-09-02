from unittest.mock import patch
from pyneuphonic.websocket import NeuphonicWebsocketClient


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
