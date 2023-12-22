import time
import random
import asyncio

from automon import log

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


class Sleeper:

    @staticmethod
    def seconds(seconds: int) -> time.sleep:
        """Sleep for this many seconds"""

        sleep = seconds
        logger.debug(f'{sleep}')
        return time.sleep(sleep)

    @staticmethod
    async def seconds_async(seconds: int) -> asyncio.sleep:
        """async Sleep for this many seconds"""

        sleep = seconds
        logger.debug(f'{sleep}')
        return await asyncio.sleep(sleep)

    @staticmethod
    def minute(minutes: int = 1) -> time.sleep:
        """Sleep for a minute"""

        sleep = round(minutes * 60)
        logger.debug(f'{sleep}')
        return time.sleep(sleep)

    @staticmethod
    async def minute_async(minutes: int = 1) -> time.sleep:
        """Sleep for a minute"""

        sleep = round(minutes * 60)
        logger.debug(f'{sleep}')
        return await asyncio.sleep(sleep)

    @staticmethod
    def within_a_minute(sleep: int = None):
        """Sleep for a random minute"""

        sleep = sleep if isinstance(sleep, int) else \
            random.choice(range(1, 1 * 60))
        logger.debug(f'{sleep}')
        return time.sleep(sleep)

    @staticmethod
    async def within_a_minute_async(sleep: int = None):
        """Sleep for a random minute"""

        sleep = sleep if isinstance(sleep, int) else \
            random.choice(range(1, 1 * 60))
        logger.debug(f'{sleep}')
        return await asyncio.sleep(sleep)

    @staticmethod
    def minutes(minutes: int):
        """Sleep for this many minutes"""

        sleep = minutes * 60
        logger.debug(f'{sleep}')
        return time.sleep(sleep)

    @staticmethod
    async def minutes_async(minutes: int):
        """Sleep for this many minutes"""

        sleep = minutes * 60
        logger.debug(f'{sleep}')
        return await asyncio.sleep(sleep)

    @staticmethod
    def hour(hour: int = 1):
        """At some time within an hour, this will run"""

        sleep = hour if not hour else random.choice(
            range(1, hour * 60 * 60))
        logger.debug(f'{sleep}')
        return time.sleep(sleep)

    @staticmethod
    async def hour_async(hour: int = 1):
        """At some time within an hour, this will run"""

        sleep = hour if not hour else random.choice(
            range(1, hour * 60 * 60))
        logger.debug(f'{sleep}')
        return await asyncio.sleep(sleep)

    @staticmethod
    def hours(hours):
        """Sleep for this many hours"""

        sleep = hours * 60 * 60
        logger.debug(f'{sleep}')
        return time.sleep(sleep)

    @staticmethod
    async def hours_async(hours):
        """Sleep for this many hours"""

        sleep = hours * 60 * 60
        logger.debug(f'{sleep}')
        return await asyncio.sleep(sleep)

    @staticmethod
    def day(hours: int = 24):
        """At some time within 24 hours, this will run"""

        sleep = hours if not hours else random.choice(
            range(1, hours * 60 * 60))
        logger.debug(f'{sleep}')
        return time.sleep(sleep)

    @staticmethod
    async def day_async(hours: int = 24):
        """At some time within 24 hours, this will run"""

        sleep = hours if not hours else random.choice(
            range(1, hours * 60 * 60))
        logger.debug(f'{sleep}')
        return await asyncio.sleep(sleep)

    @staticmethod
    def daily(hours: int = 24):
        """Sleep for one day"""

        sleep = hours if not hours else hours * 60 * 60
        logger.debug(f'{sleep}')
        return time.sleep(sleep)

    @staticmethod
    async def daily_async(hours: int = 24):
        """Sleep for one day"""

        sleep = hours if not hours else hours * 60 * 60
        logger.debug(f'{sleep}')
        return await asyncio.sleep(sleep)

    @staticmethod
    def time_range(seconds: int):
        """Sleep for a random range"""

        sleep = seconds if not seconds else random.choice(
            range(1, seconds))
        logger.debug(f'{sleep}')
        return time.sleep(sleep)

    @staticmethod
    async def time_range_async(seconds: int):
        """Sleep for a random range"""

        sleep = seconds if not seconds else random.choice(
            range(1, seconds))
        logger.debug(f'{sleep}')
        return await asyncio.sleep(sleep)
