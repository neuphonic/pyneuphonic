"""
Defines fixtures used by a variety of testing files.

This file is automatically discovered by pytest and is injected into whichever test requires any
of these fixtures.
"""

import pytest
from pyneuphonic.websocket import NeuphonicWebsocketClient
import random
from unittest.mock import patch, MagicMock, AsyncMock


@pytest.fixture
def on_message():
    async def _on_message(self, message):
        pass

    return _on_message


@pytest.fixture
def on_open():
    async def _on_open(self):
        pass

    return _on_open


@pytest.fixture
def on_close():
    async def _on_close(self):
        pass

    return _on_close


@pytest.fixture
def on_error():
    async def _on_error(self, e):
        pass

    return _on_error


@pytest.fixture
def on_send():
    async def _on_send(self, message):
        pass

    return _on_send


@pytest.fixture(scope='session', autouse=True)
def patch_find_spec():
    with patch('importlib.util.find_spec', return_value=MagicMock()):
        yield


@pytest.fixture
def client(
    on_message,
    on_open,
    on_close,
    on_error,
    on_send,
):
    client = NeuphonicWebsocketClient(
        NEUPHONIC_API_TOKEN='test_token',
        NEUPHONIC_API_URL='eu-west-1.api.test.com',
        on_message=on_message,
        on_open=on_open,
        on_close=on_close,
        on_error=on_error,
        on_send=on_send,
        timeout=random.randint(5, 20),
    )

    # Ensure PyAudio-related methods are mocked
    client.setup_pyaudio = AsyncMock()
    client.teardown_pyaudio = AsyncMock()
    client.play_audio = AsyncMock()

    return client


@pytest.fixture
def unsecure_client(
    on_message,
    on_open,
    on_close,
    on_error,
    on_send,
):
    client = NeuphonicWebsocketClient(
        NEUPHONIC_API_TOKEN='test_token',
        NEUPHONIC_API_URL='localhost:8080',
        on_message=on_message,
        on_open=on_open,
        on_close=on_close,
        on_error=on_error,
        on_send=on_send,
        timeout=random.randint(5, 20),
    )

    # Ensure PyAudio-related methods are mocked
    client.setup_pyaudio = AsyncMock()
    client.teardown_pyaudio = AsyncMock()
    client.play_audio = AsyncMock()

    return client
