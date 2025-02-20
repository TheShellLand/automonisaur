import re
import random
import selenium.webdriver

from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO
from automon.helpers.osWrapper import environ

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


class SeleniumConfig(object):
    def __init__(self):
        self._webdriver = None
        self.webdriver_wrapper = None

        self.cookies_autosave: bool = environ('SELENIUM_COOKIES_AUTOSAVE', False)
        self._cookies_base64 = environ('SELENIUM_COOKIES_BASE64')
        self._cookies_file = environ('SELENIUM_COOKIES_FILE')

        self.proxies = []
        self.use_random_proxy = False

    def add_proxy(self, proxy: str):
        """add proxy"""

        if not re.compile(r'\d+.\d+.\d+.\d+:\d+').match(proxy):
            raise ValueError(f'SeleniumConfig :: add proxy :: ERROR :: bad proxy format (e.g. IP:PORT) :: {proxy=}')

        self.proxies.append(proxy)

        logger.debug(f'SeleniumConfig :: add proxy :: {proxy}')
        logger.info(f'SeleniumConfig :: add proxy :: DONE')
        return self

    def delete_proxies(self):
        self.proxies = []
        logger.info(f'SeleniumConfig :: delete proxies :: DONE')
        return self

    def get_random_proxy(self) -> str:
        """get random proxy"""
        if self.proxies:
            proxy = random.choice(self.proxies)
            logger.debug(f'SeleniumConfig :: get random proxy :: {proxy}')
            return proxy

    def get_proxy(self) -> dict:
        """get first proxy"""
        if self.proxies:
            proxy = self.proxies[0]
            logger.debug(f'SeleniumConfig :: get proxy :: {proxy}')
            return proxy

    @property
    def webdriver(self):
        try:
            return self.webdriver_wrapper.webdriver
        except:
            return self._webdriver

    @property
    def window_size(self):
        """get window size"""
        if self.webdriver_wrapper:
            return self.webdriver_wrapper.window_size

    @property
    def cookies_base64(self):
        logger.debug(
            f'SeleniumConfig :: cookies base64 :: {len(self._cookies_base64) / 1024 if self._cookies_base64 else None} KB')
        return self._cookies_base64

    @property
    def cookies_file(self):
        logger.debug(f'SeleniumConfig :: cookies file :: {self._cookies_file}')
        return self._cookies_file

    def run(self):
        """run webdriver"""
        logger.debug(f'SeleniumConfig :: run')

        if self.proxies:
            if self.use_random_proxy:
                proxy = self.get_random_proxy()
            else:
                proxy = self.get_proxy()

            logger.debug(f'SeleniumConfig :: run :: add proxy :: {proxy}')
            self.webdriver_wrapper.enable_proxy(proxy=proxy)

        run = self.webdriver_wrapper.run()
        self._webdriver = self.webdriver_wrapper.webdriver
        logger.debug(f'SeleniumConfig :: run :: {self.webdriver=}')
        logger.info(f'SeleniumConfig :: run :: DONE')
        return run

    def start(self):
        """alias to run"""
        return self.run()

    def quit(self):
        """quit webdriver"""
        return NotImplemented
