import selenium.webdriver

from automon.log import Logging

from .config_webdriver import ConfigWebdriver

log = Logging(name='SeleniumConfig', level=Logging.INFO)


class SeleniumConfig(object):
    webdriver_wrapper: ConfigWebdriver

    def __init__(self):
        self._webdriver_wrapper = ConfigWebdriver()

    def __repr__(self):
        return f'{self.driver}'

    @property
    def set_webdriver(self):
        return self._webdriver_wrapper

    @property
    def driver(self):
        return self.webdriver

    @property
    def webdriver(self):
        if self.set_webdriver.webdriver:
            return self.set_webdriver.webdriver
        else:
            log.error('driver not set. configure a driver first')
