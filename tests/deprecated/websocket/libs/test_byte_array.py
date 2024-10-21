import pytest
from pyneuphonic.websocket.libs import SubscriptableAsyncByteArray
from unittest.mock import AsyncMock, call


@pytest.mark.asyncio
async def test_subscriptable_byte_array():
    # create byte array
    byte_array = SubscriptableAsyncByteArray()

    # create and subscribe a couple of callbacks
    callback_function_1 = AsyncMock()
    callback_function_2 = AsyncMock()

    byte_array.subscribe(callback_function_1)
    byte_array.subscribe(callback_function_2)

    # extend with some test data
    data_1 = b'audio data 1'
    data_2 = b'audio data 2'

    await byte_array.extend(data_1)
    await byte_array.extend(data_2)

    # assert that the callback functions were called with the correct data
    callback_function_1.assert_has_calls([call(data_1), call(data_2)])
    callback_function_2.assert_has_calls([call(data_1), call(data_2)])
