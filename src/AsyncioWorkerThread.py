import asyncio
import threading
from collections.abc import Generator
from threading import Thread
from typing import Coroutine, Awaitable


class AsyncioWorkerThread(Thread):

    def __init__(self):
        super().__init__()
        self._loop = asyncio.new_event_loop()
        self._shutdown_event = threading.Event()

    async def _shutdown_check(self):
        while True:
            if self._shutdown_event.is_set():
                self._loop.stop()
            await asyncio.sleep(10)

    def add_task(self, coro: Coroutine | Awaitable | Generator):
        return asyncio.run_coroutine_threadsafe(coro, self._loop)

    def stop(self):
        self._shutdown_event.set()

    def run(self):
        self._shutdown_event.clear()
        self._loop.create_task(self._shutdown_check())
        self._loop.run_forever()
