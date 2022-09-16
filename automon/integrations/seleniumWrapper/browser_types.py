import selenium

from automon.log import Logging

from .config import SeleniumConfig

log = Logging(name='BrowserType', level=Logging.DEBUG)


class BrowserType(object):

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
    def edge(self):
        log.info(f'Browser set as Edge')
        return self.webdriver.Edge()

    @property
    def firefox(self):
        log.info(f'Browser set as Firefox')
        return self.webdriver.Firefox()

    @property
    def ie(self):
        log.info(f'Browser set as Internet Explorer')
        return self.webdriver.Ie()

    @property
    def opera(self):
        log.info(f'Browser set as Opera')
        return self.webdriver.Opera()

    @property
    def proxy(self):
        log.info(f'Browser using proxy')
        return self.webdriver.Proxy()

    @property
    def remote(self):
        log.info(f'Browser using remote browser')
        return self.webdriver.Remote()

    @property
    def safari(self):
        log.info(f'Browser set as Safari')
        return self.webdriver.Safari()

    @property
    def webkit_gtk(self):
        log.info(f'Browser set as WebKitGTK')
        return self.webdriver.WebKitGTK()

    @property
    def wpewebkit(self):
        log.info(f'Browser set as WPEWebKit')
        return self.webdriver.WPEWebKit()
