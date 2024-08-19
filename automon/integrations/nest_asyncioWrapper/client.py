import asyncio
import nest_asyncio

from automon import log

logger = log.logging.getLogger(__name__)
logger.setLevel(log.ERROR)

log.logging.getLogger("asyncio").setLevel(log.ERROR)


class AsyncStarter:

    def __init__(self) -> asyncio.get_event_loop:

        self.event_loop = asyncio.get_event_loop()
        self.maxqueue = 1000
        self.queue = asyncio.Queue(maxsize=self.maxqueue)
        self._nest = nest_asyncio.apply()
        asyncio.run(self._coro())

        self._finished = None

    async def _coro(self) -> asyncio:
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

    def run(self) -> asyncio:
        asyncio.run(self._coro())

    def start(self) -> run:
        return self.run()

    def create_task(self, task):
        return self.event_loop.create_task(task)
