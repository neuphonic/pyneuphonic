import asyncio
from typing import Callable, Awaitable


class SubscriptableAsyncByteArray(bytearray):
    def __init__(self):
        """
        A wrapper around the python bytearray object, providing subscription capabilities in an async way.
        """
        super().__init__()
        # self.byte_data = bytearray()
        self.subscribers = []
        self.notify_lock = asyncio.Lock()

    def subscribe(self, callback: Callable[[bytes], Awaitable]):
        """
        Subscribe to any updates to the byte_data with a callback function.

        Parameters
        ----------
        callback : : Callable[[bytes], Awaitable]
            The callback function. Takes the newly appended bytes and processes them. Must be an async function.
        """
        self.subscribers.append(callback)

    async def extend(self, new_bytes):
        super().extend(new_bytes)

        async with self.notify_lock:
            await self._notify_subscribers(new_bytes)

    async def _notify_subscribers(self, new_bytes):
        await asyncio.gather(*(callback(new_bytes) for callback in self.subscribers))