import time
import random

from automon.log.logger import Logging

log = Logging(__name__, level=Logging.INFO)


class Sleeper:

    @staticmethod
    def seconds(caller: object or str, seconds: int) -> time.sleep:
        """Sleep for this many seconds"""

        sleep = seconds
        log.info(f'[{Sleeper.seconds.__name__}] [{caller}] sleeping for {sleep} seconds')
        return time.sleep(sleep)

    @staticmethod
    def minute(caller: object or str, sleep: int = 60) -> time.sleep:
        """Sleep for a minute"""

        log.info(f'[{Sleeper.minute.__name__}] [{caller}] sleeping for {sleep} seconds')
        return time.sleep(sleep)

    @staticmethod
    def within_a_minute(caller, sleep: int = None):
        """Sleep for a random minute"""

        sleep = sleep if isinstance(sleep, int) else random.choice(range(1, 1 * 60))
        log.info(f'[{Sleeper.within_a_minute.__name__}] [{caller}] sleeping for {sleep} seconds')
        return time.sleep(sleep)

    @staticmethod
    def minutes(caller, minutes: int):
        """Sleep for this many minutes"""

        sleep = minutes * 60
        log.info(f'[{Sleeper.minutes.__name__}] [{caller}] sleeping for {sleep} minutes')
        return time.sleep(sleep)

    @staticmethod
    def hour(caller, hour: int = 1):
        """At some time within an hour, this will run"""

        sleep = hour if not hour else random.choice(
            range(1, hour * 60 * 60))
        log.info(f'[{Sleeper.hour.__name__}] [{caller}] sleeping for {sleep} seconds')
        return time.sleep(sleep)

    @staticmethod
    def hours(caller, hours):
        """Sleep for this many hours"""

        sleep = hours * 60 * 60
        log.info(f'[{Sleeper.hours.__name__}] [{caller}] sleeping for {hours} hours')
        return time.sleep(sleep)

    @staticmethod
    def day(caller, hours: int = 24):
        """At some time within 24 hours, this will run"""

        sleep = hours if not hours else random.choice(
            range(1, hours * 60 * 60))
        log.info(f'[{Sleeper.day.__name__}] [{caller}] sleeping for {sleep} seconds')
        return time.sleep(sleep)

    @staticmethod
    def daily(caller, hours: int = 24):
        """Sleep for one day"""

        sleep = hours if not hours else hours * 60 * 60
        log.info(f'[{Sleeper.daily.__name__}] [{caller}] sleeping for {sleep} seconds')
        return time.sleep(sleep)

    @staticmethod
    def time_range(caller, seconds: int):
        """Sleep for a random range
        """
        sleep = seconds if not seconds else random.choice(
            range(1, seconds))
        log.info(f'[{Sleeper.time_range.__name__}] [{caller}] sleeping for {sleep} seconds')
        return time.sleep(sleep)
