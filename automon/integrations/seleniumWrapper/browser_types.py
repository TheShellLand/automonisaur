import selenium
import selenium.webdriver.chrome.options

from selenium.webdriver import Chrome
from selenium.webdriver import Edge
from selenium.webdriver import Firefox
from selenium.webdriver import Ie
from selenium.webdriver import Proxy
from selenium.webdriver import Remote
from selenium.webdriver import Safari
from selenium.webdriver import WebKitGTK

from automon.log import Logging

from .config import SeleniumConfig

# fix for python36
try:
    import selenium.webdriver.chromium.options
    from selenium.webdriver import ChromiumEdge
    from selenium.webdriver import WPEWebKit
except:
    from selenium.webdriver import Chrome as ChromiumEdge
    from selenium.webdriver import Chrome as WPEWebKit


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
    def chrome(self, options: list = None) -> Chrome:
        """Chrome"""
        log.info(f'Browser set as Chrome')

        chrome_options = selenium.webdriver.chrome.options.Options()

        if options:
            for arg in options:
                chrome_options.add_argument(arg)

        try:
            if self.chromedriver:
                return self.webdriver.Chrome(self.chromedriver, options=chrome_options)
            return self.webdriver.Chrome(options=chrome_options)
        except Exception as e:
            log.error(f'Browser not set. {e}', enable_traceback=False)

    @property
    def chrome_headless(self, options: list = None, **kwargs) -> Chrome:
        """Chrome headless

        chrome_options = Options()
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox") # linux only
        chrome_options.add_argument("--headless")

        chrome_options.headless = True # also works

        """
        log.info(f'Browser set as Chrome Headless')

        chrome_options = selenium.webdriver.chrome.options.Options()
        chrome_options.headless = True

        if options:
            for arg in options:
                chrome_options.add_argument(arg)

        try:
            if self.chromedriver:
                return self.webdriver.Chrome(self.chromedriver, options=chrome_options, **kwargs)
            return self.webdriver.Chrome(options=chrome_options, **kwargs)
        except Exception as e:
            log.error(f'Browser not set. {e}', enable_traceback=False)

    @property
    def chromium_edge(self, options: list = None, **kwargs) -> ChromiumEdge:
        """Chromium"""
        log.info(f'Browser set as Chromium Edge')

        chromium_options = selenium.webdriver.chromium.options.ChromiumOptions()

        if options:
            for arg in options:
                chromium_options.add_argument(arg)

        try:
            if self.chromedriver:
                return self.webdriver.ChromiumEdge(self.chromedriver, options=chromium_options, **kwargs)
            return self.webdriver.ChromiumEdge(options=chromium_options, **kwargs)
        except Exception as e:
            log.error(f'Browser not set. {e}', enable_traceback=False)

    @property
    def edge(self, **kwargs) -> Edge:
        """Edge"""
        log.info(f'Browser set as Edge')
        return self.webdriver.Edge(**kwargs)

    @property
    def firefox(self, **kwargs) -> Firefox:
        """Firefox"""
        log.info(f'Browser set as Firefox')
        return self.webdriver.Firefox(**kwargs)

    @property
    def ie(self, **kwargs) -> Ie:
        """Internet Explorer"""
        log.info(f'Browser set as Internet Explorer')
        return self.webdriver.Ie(**kwargs)

    @property
    def opera(self):
        """Depreciated: Opera"""
        log.warn(f'Opera is depreciated')

    @property
    def proxy(self, **kwargs) -> Proxy:
        """Proxy"""
        log.info(f'Browser using proxy')
        return self.webdriver.Proxy(**kwargs)

    @property
    def phantomjs(self):
        """PhantomJS"""
        log.warn(f'PhantomJS not supported')

    @property
    def remote(self, **kwargs) -> Remote:
        """Remote"""
        log.info(f'Browser using remote browser')
        return self.webdriver.Remote(**kwargs)

    @property
    def safari(self, **kwargs) -> Safari:
        """Safari"""
        log.info(f'Browser set as Safari')
        return self.webdriver.Safari(**kwargs)

    @property
    def webkit_gtk(self, **kwargs) -> WebKitGTK:
        """WebKit GTK"""
        log.info(f'Browser set as WebKitGTK')
        return self.webdriver.WebKitGTK(**kwargs)

    @property
    def wpewebkit(self, **kwargs) -> WPEWebKit:
        """WPE WebKit"""
        log.info(f'Browser set as WPEWebKit')
        return self.webdriver.WPEWebKit(**kwargs)
