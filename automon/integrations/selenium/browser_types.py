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
        return ''

    @property
    def chrome(self):
        log.info(f'Browser set as Chrome')
        return self.webdriver.Chrome(self.chromedriver)

    @property
    def chromium_edge(self):
        log.info(f'Browser set as Chromium Edge')
        return self.webdriver.ChromiumEdge(self.chromedriver)

    @property
    def edge(self):
        log.info(f'Browser set as Edge')
        return self.webdriver.Edge(self.chromedriver)

    @property
    def firefox(self):
        log.info(f'Browser set as Firefox')
        return self.webdriver.Firefox(self.chromedriver)

    @property
    def ie(self):
        log.info(f'Browser set as Internet Explorer')
        return self.webdriver.Ie(self.chromedriver)

    @property
    def opera(self):
        log.info(f'Browser set as Opera')
        return self.webdriver.Opera(self.chromedriver)

    @property
    def proxy(self):
        log.info(f'Browser using proxy')
        return self.webdriver.Proxy(self.chromedriver)

    @property
    def remote(self):
        log.info(f'Browser using remote browser')
        return self.webdriver.Remote(self.chromedriver)

    @property
    def safari(self):
        log.info(f'Browser set as Safari')
        return self.webdriver.Safari(self.chromedriver)

    @property
    def webkit_gtk(self):
        log.info(f'Browser set as WebKitGTK')
        return self.webdriver.WebKitGTK(self.chromedriver)

    @property
    def wpewebkit(self):
        log.info(f'Browser set as WPEWebKit')
        return self.webdriver.WPEWebKit(self.chromedriver)
