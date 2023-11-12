import time
import random

from automon.log import logger

log = logger.logging.getLogger(__name__)
log.setLevel(logger.DEBUG)


class Sleeper:

    @staticmethod
    def seconds(seconds: int) -> time.sleep:
        """Sleep for this many seconds"""

        sleep = seconds
        log.debug(f'{sleep}')
        return time.sleep(sleep)

    @staticmethod
    def minute(minutes: int = 1) -> time.sleep:
        """Sleep for a minute"""

        sleep = round(minutes * 60)
        log.debug(f'{sleep}')
        return time.sleep(sleep)

    @staticmethod
    def within_a_minute(sleep: int = None):
        """Sleep for a random minute"""

        sleep = sleep if isinstance(sleep, int) else \
            random.choice(range(1, 1 * 60))
        log.debug(f'{sleep}')
        return time.sleep(sleep)

    @staticmethod
    def minutes(minutes: int):
        """Sleep for this many minutes"""

        sleep = minutes * 60
        log.debug(f'{sleep}')
        return time.sleep(sleep)

    @staticmethod
    def hour(hour: int = 1):
        """At some time within an hour, this will run"""

        sleep = hour if not hour else random.choice(
            range(1, hour * 60 * 60))
        log.debug(f'{sleep}')
        return time.sleep(sleep)

    @staticmethod
    def hours(hours):
        """Sleep for this many hours"""

        sleep = hours * 60 * 60
        log.debug(f'{sleep}')
        return time.sleep(sleep)

    @staticmethod
    def day(hours: int = 24):
        """At some time within 24 hours, this will run"""

        sleep = hours if not hours else random.choice(
            range(1, hours * 60 * 60))
        log.debug(f'{sleep}')
        return time.sleep(sleep)

    @staticmethod
    def daily(hours: int = 24):
        """Sleep for one day"""

        sleep = hours if not hours else hours * 60 * 60
        log.debug(f'{sleep}')
        return time.sleep(sleep)

    @staticmethod
    def time_range(seconds: int):
        """Sleep for a random range"""

        sleep = seconds if not seconds else random.choice(
            range(1, seconds))
        log.debug(f'{sleep}')
        return time.sleep(sleep)
