import selenium.webdriver

from automon.log import logger

from .config_webdriver_chrome import ConfigChrome

log = logger.logging.getLogger(__name__)
log.setLevel(logger.DEBUG)


class ConfigWebdriver(object):
    webdriver: selenium.webdriver
    webdriver_wrapper: any

    Chrome: ConfigChrome
    Edge: NotImplemented
    Firefox: NotImplemented

    def __init__(self):
        self._webdriver_wrapper = None

        self._chrome = ConfigChrome()
        self._edge = NotImplemented
        self._firefox = NotImplemented

    def __repr__(self):
        if self._webdriver_wrapper:
            return f'{self._webdriver_wrapper}'
        return f'webdriver not configured. try selecting a webdriver'

    @property
    def driver(self):
        """alias to webdriver

        """
        return self.webdriver

    @property
    def webdriver(self):
        """selenium webdriver

        """
        return self.webdriver_wrapper.webdriver

    @property
    def webdriver_wrapper(self) -> any or ConfigChrome:
        """webdriver wrapper

        """
        return self._webdriver_wrapper

    @property
    def window_size(self):
        """get window size

        """
        if self.webdriver_wrapper:
            return self.webdriver_wrapper.window_size

    def Chrome(self):
        """selenium Chrome webdriver

        """
        self._webdriver_wrapper = self._chrome
        return self._webdriver_wrapper

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
        try:
            return self.webdriver_wrapper.run()
        except Exception as e:
            log.error(f'failed to run: {e}')

    def start(self):
        """alias to run"""
        return self.run()

    def quit(self):
        """quit webdriver"""
        return
