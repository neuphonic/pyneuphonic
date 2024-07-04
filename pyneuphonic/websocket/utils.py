import asyncio


class SubscriptableByteArray:
    def __init__(self):
        self.byte_data = bytearray()
        self.subscribers = []
        self.notify_lock = asyncio.Lock()

    def subscribe(self, callback):
        self.subscribers.append(callback)

    async def append(self, new_bytes):
        self.byte_data.extend(new_bytes)
        async with self.notify_lock:
            await self._notify_subscribers(new_bytes)

    async def _notify_subscribers(self, new_bytes):
        await asyncio.gather(*(callback(new_bytes) for callback in self.subscribers))
