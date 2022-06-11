from automon.log import Logging

log = Logging(name='BrowserType', level=Logging.DEBUG)


class BrowserType(object):

    @property
    def chrome(self):
        return self.webdriver.Chrome()

    @property
    def chromium_edge(self):
        return self.webdriver.ChromiumEdge()

    @property
    def edge(self):
        return self.webdriver.Edge()

    @property
    def firefox(self):
        return self.webdriver.Firefox()

    @property
    def ie(self):
        return self.webdriver.Ie()

    @property
    def opera(self):
        return self.webdriver.Opera()

    @property
    def proxy(self):
        return self.webdriver.Proxy()

    @property
    def remote(self):
        return self.webdriver.Remote()

    @property
    def safari(self):
        return self.webdriver.Safari()

    @property
    def webkit_gtk(self):
        return self.webdriver.WebKitGTK()

    @property
    def wpewebkit(self):
        return self.webdriver.WPEWebKit()
