import selenium.webdriver

from automon import log
from automon.helpers.osWrapper import environ

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


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
        logger.debug(f'{len(self._cookies_base64) if self._cookies_base64 else None}')
        return self._cookies_base64

    @property
    def cookies_file(self):
        logger.info(f'{self._cookies_file}')
        return self._cookies_file

    async def run(self):
        """run webdriver"""
        run = await self.webdriver_wrapper.run()
        self._webdriver = self.webdriver_wrapper.webdriver
        logger.info(str(dict(
            webdriver=self.webdriver
        )))
        return run

    async def start(self):
        """alias to run"""
        return await self.run()

    async def quit(self):
        """quit webdriver"""
        return
