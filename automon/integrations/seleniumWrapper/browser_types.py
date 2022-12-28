import selenium
import selenium.webdriver.chrome.options
import selenium.webdriver.chromium.options

from selenium.webdriver import (Chrome, ChromiumEdge, Edge, Firefox, Ie, Proxy, Remote, Safari, WebKitGTK, WPEWebKit)

from automon.log import Logging

from .config import SeleniumConfig

log = Logging(name='BrowserType', level=Logging.DEBUG)


class BrowserType(object):
    config: SeleniumConfig

    def __init__(self, config: SeleniumConfig):
        self.config = config
        self.webdriver = self.config.webdriver
        self.chromedriver = self.config.selenium_chromedriver_path

    def __repr__(self):
        return 'BrowserType'

    @property
    def chrome(self):
        log.info(f'Browser set as Chrome')
        try:
            if self.chromedriver:
                return self.webdriver.Chrome(self.chromedriver)
            return self.webdriver.Chrome()
        except Exception as e:
            log.error(f'Browser not set. {e}', enable_traceback=False)

    @property
    def chromium_edge(self):
        log.info(f'Browser set as Chromium Edge')
        try:
            if self.chromedriver:
                return self.webdriver.ChromiumEdge(self.chromedriver)
            return self.webdriver.ChromiumEdge()
        except Exception as e:
            log.error(f'Browser not set. {e}', enable_traceback=False)

    @property
    def edge(self, **kwargs):
        """Edge"""
        log.info(f'Browser set as Edge')
        return self.webdriver.Edge(**kwargs)

    @property
    def firefox(self, **kwargs):
        """Firefox"""
        log.info(f'Browser set as Firefox')
        return self.webdriver.Firefox(**kwargs)

    @property
    def ie(self, **kwargs):
        """Internet Explorer"""
        log.info(f'Browser set as Internet Explorer')
        return self.webdriver.Ie(**kwargs)

    @property
    def opera(self, **kwargs):
        """Depreciated: Opera"""
        log.warn(f'Opera is depreciated')

    @property
    def proxy(self, **kwargs):
        """Proxy"""
        log.info(f'Browser using proxy')
        return self.webdriver.Proxy(**kwargs)

    @property
    def phantomjs(self):
        """PhantomJS"""
        log.warn(f'PhantomJS not supported')

    @property
    def remote(self, **kwargs):
        """Remote"""
        log.info(f'Browser using remote browser')
        return self.webdriver.Remote(**kwargs)

    @property
    def safari(self, **kwargs):
        """Safari"""
        log.info(f'Browser set as Safari')
        return self.webdriver.Safari(**kwargs)

    @property
    def webkit_gtk(self, **kwargs):
        """WebKit GTK"""
        log.info(f'Browser set as WebKitGTK')
        return self.webdriver.WebKitGTK(**kwargs)

    @property
    def wpewebkit(self, **kwargs):
        """WPE WebKit"""
        log.info(f'Browser set as WPEWebKit')
        return self.webdriver.WPEWebKit(**kwargs)
