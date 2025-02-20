import random

from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(INFO)


class RequestsConfig(object):

    def __init__(self, use_random_proxies: bool = False):
        self.proxies = []
        self.use_random_proxies = use_random_proxies

        # $ export HTTP_PROXY="http://10.10.1.10:3128"
        # $ export HTTPS_PROXY="http://10.10.1.10:1080"
        # $ export ALL_PROXY="socks5://10.10.1.10:3434"

    def __repr__(self):
        return f'{len(self.proxies)} proxies'

    def add_proxy(self, proxy: str):
        """add proxy"""
        new_proxy = self.create_proxy(http=proxy, https=proxy, ftp=proxy)
        if new_proxy not in self.proxies:
            logger.debug(f'RequestsConfig :: ADD PROXY :: {new_proxy}')
            self.proxies.append(new_proxy)

        logger.info(f'RequestsConfig :: ADD PROXY :: DONE')
        return self

    @staticmethod
    def create_proxy(http: str = None, https: str = None, ftp: str = None):
        """create proxy"""
        proxy = dict(
            http=http,
            https=https,
            ftp=ftp,
        )
        logger.debug(f'RequestsConfig :: CREATE PROXY :: {proxy}')

    def delete_proxies(self):
        self.proxies = []
        logger.info(f'RequestsConfig :: DELETE PROXIES :: DONE')
        return self

    def get_random_proxy(self) -> dict:
        """get random proxy"""
        if self.proxies:
            return random.choice(self.proxies)

    def get_proxy(self) -> dict:
        """get first proxy"""
        if self.proxies:
            return self.proxies[0]

    @property
    def is_ready(self):
        return f'{NotImplemented}'
