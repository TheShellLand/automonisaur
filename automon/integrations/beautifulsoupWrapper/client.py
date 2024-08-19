from bs4 import BeautifulSoup

from automon import log

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


class BeautifulSoupClient(object):

    def __init__(self, bs: BeautifulSoup = None):
        self.bs = bs

    def read_markup(self, markup: str, features: str = 'lxml'):
        """read markup with beautifulsoup"""
        try:
            self.bs = BeautifulSoup(
                markup=markup or self.markup,
                features=features
            )
            logger.info(f'read_markup success ({len(markup)} B)')
        except Exception as e:
            logger.error(f'read_markup failed ({len(markup)} B): {e}')

        return self
