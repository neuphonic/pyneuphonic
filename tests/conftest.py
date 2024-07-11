"""
Defines fixtures used by a variety of testing files.

This file is automatically discovered by pytest and is injected into whichever test requires any
of these fixtures.
"""

import pytest
from pyneuphonic.websocket import NeuphonicWebsocketClient
import random


@pytest.fixture
def on_audio_message():
    async def _on_audio_message(self, message):
        pass

    return _on_audio_message


@pytest.fixture
def on_non_audio_message():
    async def _on_non_audio_message(self, message):
        pass

    return _on_non_audio_message


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
def on_ping():
    async def _on_ping(self):
        pass

    return _on_ping


@pytest.fixture
def on_pong():
    async def _on_pong(self):
        pass

    return _on_pong


@pytest.fixture
def on_send():
    async def _on_send(self, message):
        pass

    return _on_send


@pytest.fixture
def client(
    on_audio_message,
    on_non_audio_message,
    on_open,
    on_close,
    on_error,
    on_ping,
    on_pong,
    on_send,
):
    return NeuphonicWebsocketClient(
        NEUPHONIC_API_TOKEN='test_token',
        NEUPHONIC_WEBSOCKET_URL='wss://test_url',
        on_audio_message=on_audio_message,
        on_non_audio_message=on_non_audio_message,
        on_open=on_open,
        on_close=on_close,
        on_error=on_error,
        on_ping=on_ping,
        on_pong=on_pong,
        on_send=on_send,
        timeout=random.randint(5, 20),
    )


@pytest.fixture
def unsecure_client(
    on_audio_message,
    on_non_audio_message,
    on_open,
    on_close,
    on_error,
    on_ping,
    on_pong,
    on_send,
):
    return NeuphonicWebsocketClient(
        NEUPHONIC_API_TOKEN='test_token',
        NEUPHONIC_WEBSOCKET_URL='ws://test_url',
        on_audio_message=on_audio_message,
        on_non_audio_message=on_non_audio_message,
        on_open=on_open,
        on_close=on_close,
        on_error=on_error,
        on_ping=on_ping,
        on_pong=on_pong,
        on_send=on_send,
        timeout=random.randint(5, 20),
    )
