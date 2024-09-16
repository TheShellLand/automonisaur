import selenium.webdriver

from automon import log
from automon.helpers.osWrapper import environ

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


class SeleniumConfig(object):
    def __init__(self):
        self._webdriver = None
        self.webdriver_wrapper = None

        self.cookies_autosave: bool = environ('SELENIUM_COOKIES_AUTOSAVE', False)
        self._cookies_base64 = environ('SELENIUM_COOKIES_BASE64')
        self._cookies_file = environ('SELENIUM_COOKIES_FILE')

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
        logger.debug(f'cookies_base64 :: {len(self._cookies_base64) / 1024 if self._cookies_base64 else None} KB')
        return self._cookies_base64

    @property
    def cookies_file(self):
        logger.debug(f'cookies_file :: {self._cookies_file}')
        return self._cookies_file

    def run(self):
        """run webdriver"""
        logger.debug(f'webdriver :: config :: run')
        run = self.webdriver_wrapper.run()
        self._webdriver = self.webdriver_wrapper.webdriver
        logger.debug(f'webdriver :: config :: run :: {self.webdriver=}')
        logger.info(f'webdriver :: config :: run :: done')
        return run

    def start(self):
        """alias to run"""
        return self.run()

    def quit(self):
        """quit webdriver"""
        return
