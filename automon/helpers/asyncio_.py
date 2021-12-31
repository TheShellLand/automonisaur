import asyncio
import logging
import nest_asyncio

from automon.log import Logging

logging.getLogger("asyncio").setLevel(Logging.ERROR)


class AsyncStarter:

    def __init__(self) -> asyncio.get_event_loop:
        self._log = Logging(name=AsyncStarter.__name__, level=Logging.DEBUG)

        self.event_loop = asyncio.get_event_loop()
        self.maxqueue = 1000
        self.queue = asyncio.Queue(maxsize=self.maxqueue)
        self._nest = nest_asyncio.apply()
        asyncio.run(self._coro())

        self._finished = None

    async def _coro(self) -> asyncio.coroutine:
        await asyncio.sleep(0)

    def run_until_complete(self):
        while True:
            if self.queue.qsize():
                asyncio.run(asyncio.sleep(0))
            else:
                self._finished = True
                break

    @staticmethod
    def sleep(seconds: int):
        asyncio.run(asyncio.sleep(seconds))

    def run(self) -> asyncio.run:
        asyncio.run(self._coro())

    def start(self) -> run:
        return self.run()

    def create_task(self, task):
        return self.event_loop.create_task(task)
