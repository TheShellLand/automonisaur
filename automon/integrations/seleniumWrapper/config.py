import selenium.webdriver

from automon.log import logger
from automon.helpers.osWrapper import environ

log = logger.logging.getLogger(__name__)
log.setLevel(logger.DEBUG)


class SeleniumConfig(object):
    def __init__(self):
        self._webdriver = None
        self.webdriver_wrapper = None

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

    def run(self):
        """run webdriver"""
        run = self.webdriver_wrapper.run()
        self._webdriver = self.webdriver_wrapper.webdriver
        log.info(str(dict(
            webdriver=self.webdriver
        )))
        return run

    def start(self):
        """alias to run"""
        return self.run()

    def quit(self):
        """quit webdriver"""
        return
