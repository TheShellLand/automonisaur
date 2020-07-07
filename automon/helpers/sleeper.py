import time
import random

from automon.logger import Logging

log = Logging('sleeper', level=Logging.INFO)


class Sleeper:

    @staticmethod
    def seconds(caller, seconds):
        """Sleep for this many seconds
        """
        sleep = seconds
        log.info(f'[{Sleeper.seconds.__name__}] [{caller}] sleeping for {sleep} seconds')
        return time.sleep(sleep)

    @staticmethod
    def minute(caller):
        """Sleep for a minute
        """
        sleep = 60
        log.info(f'[{Sleeper.minute.__name__}] [{caller}] sleeping for {sleep} seconds')
        return time.sleep(sleep)

    @staticmethod
    def within_a_minute(caller):
        """Sleep for a random minute
        """
        sleep = random.choice(range(1, 1 * 60))
        log.info(f'[{Sleeper.within_a_minute.__name__}] [{caller}] sleeping for {sleep} seconds')
        return time.sleep(sleep)

    @staticmethod
    def minutes(caller, minutes):
        """Sleep for this many minutes
        """
        sleep = minutes * 60
        log.info(f'[{Sleeper.minutes.__name__}] [{caller}] sleeping for {sleep} minutes')
        return time.sleep(sleep)

    @staticmethod
    def hour(caller):
        """At some time within an hour, this will run
        """
        sleep = random.choice(range(1, 1 * 60 * 60))
        log.info(f'[{Sleeper.hour.__name__}] [{caller}] sleeping for {sleep} seconds')
        return time.sleep(sleep)

    @staticmethod
    def hours(caller, hours):
        """Sleep for this many hours
        """
        sleep = hours * 60 * 60
        log.info(f'[{Sleeper.hours.__name__}] [{caller}] sleeping for {hours} hours')
        return time.sleep(sleep)

    @staticmethod
    def day(caller):
        """At some time within 24 hours, this will run
        """
        sleep = random.choice(range(1, 24 * 60 * 60))
        log.info(f'[{Sleeper.day.__name__}] [{caller}] sleeping for {sleep} seconds')
        return time.sleep(sleep)

    @staticmethod
    def daily(caller):
        """Sleep for one day
        """
        sleep = 24 * 60 * 60
        log.info(f'[{Sleeper.daily.__name__}] [{caller}] sleeping for {sleep} seconds')
        return time.sleep(sleep)

    @staticmethod
    def time_range(caller, seconds):
        """Sleep for a random range
        """
        sleep = random.choice(range(1, seconds))
        log.info(f'[{Sleeper.time_range.__name__}] [{caller}] sleeping for {sleep} seconds')
        return time.sleep(sleep)
