from bs4 import BeautifulSoup

from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


class BeautifulSoupClient(object):
    BeautifulSoup = BeautifulSoup

    def __init__(self,
                 bs: BeautifulSoup = None,
                 markup: str = None):
        self.bs = bs
        self.markup = markup

    def read_markup(self, markup: str, features: str = 'lxml'):
        """read markup with beautifulsoup"""
        try:
            self.bs = BeautifulSoup(
                markup=markup,
                features=features
            )
            self.markup = markup
            logger.info(f'read_markup success ({len(markup)} B)')
        except Exception as e:
            logger.error(f'read_markup failed ({len(markup)} B): {e}')

        return self
