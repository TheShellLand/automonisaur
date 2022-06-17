import selenium

from automon.log import Logging

log = Logging(name='BrowserType', level=Logging.DEBUG)


class BrowserType(object):

    def __init__(self, webdriver: selenium.webdriver):
        self.webdriver = webdriver

    def __repr__(self):
        return ''

    @property
    def chrome(self):
        log.info(f'Browser set as Chrome')
        return self.webdriver.Chrome()

    @property
    def chromium_edge(self):
        log.info(f'Browser set as Chromium Edge')
        return self.webdriver.ChromiumEdge()

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
