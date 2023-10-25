import selenium.webdriver

from automon.log import logger

from .config_webdriver import ConfigWebdriver

log = logger.logging.getLogger(__name__)
log.setLevel(logger.DEBUG)


class SeleniumConfig(object):
    webdriver_wrapper: ConfigWebdriver

    def __init__(self):
        self._webdriver_wrapper = ConfigWebdriver()

    def __repr__(self):
        return f'{self.driver}'

    # @property
    # def driver(self):
    #     return self.webdriver

    @property
    def set_webdriver(self):
        return self._webdriver_wrapper

    @property
    def webdriver(self):
        if self.set_webdriver.webdriver:
            return self.set_webdriver.webdriver
        else:
            log.debug('waiting for driver')
