import selenium.webdriver

from automon.log import logger
from automon.helpers.osWrapper import environ

from .config_webdriver_chrome import ConfigChrome

log = logger.logging.getLogger(__name__)
log.setLevel(logger.DEBUG)


class SeleniumConfig(object):
    def __init__(self):
        self._webdriver = None
        self._webdriver_wrapper = None

        self._cookies_base64 = environ('SELENIUM_COOKIES_BASE64')
        self._cookies_file = environ('SELENIUM_COOKIES_FILE')

        self._chrome = ConfigChrome()
        self._edge = NotImplemented
        self._firefox = NotImplemented

    @property
    def webdriver(self):
        try:
            return self.webdriver_wrapper.webdriver
        except:
            return self._webdriver

    @property
    def webdriver_wrapper(self):
        return self._webdriver_wrapper

    @property
    def window_size(self):
        """get window size

        """
        if self.webdriver_wrapper:
            return self.webdriver_wrapper.window_size

    @property
    def cookies_base64(self):
        log.debug(f'{len(self._cookies_base64) if self._cookies_base64 else None}')
        return self._cookies_base64

    @property
    def cookies_file(self):
        log.info(f'{self._cookies_file}')
        return self._cookies_file

    def Chrome(self):
        """selenium Chrome webdriver

        """
        self._webdriver_wrapper = self._chrome
        log.info(str(dict(
            webdriver_wrapper=self._webdriver_wrapper
        )))
        return self.webdriver_wrapper

    def Edge(self):
        """selenium Edge webdriver

        """
        return self._edge

    def Firefox(self):
        """selenium Firefox webdriver

        """
        return self._firefox

    def run(self):
        """run webdriver"""
        run = self.webdriver_wrapper.run()
        self._webdriver = self.webdriver_wrapper.webdriver
        log.info(str(dict(
            webdriver=self.webdriver
        )))
        return run

    def set_webdriver(self):
        return self

    def start(self):
        """alias to run"""
        return self.run()

    def quit(self):
        """quit webdriver"""
        return
