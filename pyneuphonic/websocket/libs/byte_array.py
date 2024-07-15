import asyncio
from typing import Callable, Awaitable


class SubscriptableAsyncByteArray(bytearray):
    def __init__(self):
        """
        A derived class on the built-in Python `bytearray` object, providing subscription capabilities.

        **Why is this class useful?**
        Incoming audio can be stored in this object so that one or multiple subscribers can be notified of the new audio
        data, and process it as required. This class is used by the pyaudio and sounddevice examples in
        `pyneuphonic.websocket.common` for storing incoming audio data and playing it in real-time.

        The class is provided for usage however required, or can be extended as needed.
        """
        super().__init__()
        self.subscribers = []
        self.notify_lock = asyncio.Lock()

    def subscribe(self, callback: Callable[[bytes], Awaitable]):
        """
        Subscribe to any updates with a callback function.

        Parameters
        ----------
        callback
            The callback function. Takes the newly appended bytes and processes them. Must be an async function taking
            a single argument (the new bytes).
        """
        self.subscribers.append(callback)

    async def extend(self, new_bytes: bytes):
        """
        Extend the bytearray with new bytes and notify subscribers.

        Subscribers are called by passing in the new bytes as an argument.

        Parameters
        ----------
        new_bytes : bytes
            The new bytes to extend the bytearray with.

        """
        super().extend(new_bytes)

        # lock this next part of code so that only 1 coroutine enters this block at a time
        async with self.notify_lock:
            await self._notify_subscribers(new_bytes)

    async def _notify_subscribers(self, new_bytes):
        await asyncio.gather(*(callback(new_bytes) for callback in self.subscribers))
