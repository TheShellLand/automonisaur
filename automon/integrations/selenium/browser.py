import os
import tempfile
import functools

from urllib.parse import urlparse

from automon.log import Logging
from automon.helpers.dates import Dates
from automon.helpers.sanitation import Sanitation

from .config import SeleniumConfig
from .browser_types import BrowserType

log = Logging(name='SeleniumBrowser', level=Logging.DEBUG)


class SeleniumBrowser(object):

    def __init__(self, config: SeleniumConfig = None):
        self.config = config or SeleniumConfig()
        self.type = self._browser_type = BrowserType(self.config)
        self.driver = 'not set'
        self.window_size = ''

        self.url = ''
        self.status = ''

    def __repr__(self):
        if self.url:
            return f'{self.browser.name} {self.status} {self.url} {self.window_size}'
        return f'{self.browser}'

    @property
    def browser(self) -> BrowserType:
        return self.driver

    @property
    def get_log(self, log_type: str = 'browser') -> list:
        return self.browser.get_log(log_type)

    def _isRunning(func):
        @functools.wraps(func)
        def wrapped(self, *args, **kwargs):
            if self.browser != 'not set':
                return func(self, *args, **kwargs)
            log.error(f'Browser is not set!', enable_traceback=False)
            return False

        return wrapped

    def _screenshot_name(self, prefix=None):
        """Generate a unique filename

        :param browser:
        :param prefix: prefix filename with a string
        :return:
        """
        title = self.browser.title
        url = self.browser.current_url
        hostname = urlparse(url).hostname

        hostname_ = Sanitation.ascii_numeric_only(hostname)
        title_ = Sanitation.ascii_numeric_only(title)
        timestamp = Dates.filename_timestamp()

        if prefix:
            prefix = Sanitation.safe_string(prefix)
            return f'{prefix}_{hostname_}_{title_}_{timestamp}.png'

        return f'{hostname_}_{title_}_{timestamp}.png'

    @_isRunning
    def close(self):
        log.info(f'Browser closed')
        self.browser.close()

    @_isRunning
    def get(self, url: str) -> bool:
        try:
            self.url = url
            self.browser.get(url)
            self.status = 'OK'
            return True
        except Exception as e:
            self.status = 'ERROR'
            log.error(f'Error getting {url}: {e}', enable_traceback=False)

        return False

    @_isRunning
    def get_page(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    @_isRunning
    def get_screenshot_as_png(self):
        return self.browser.get_screenshot_as_png()

    @_isRunning
    def get_screenshot_as_base64(self):
        return self.browser.get_screenshot_as_base64()

    @_isRunning
    def save_screenshot(self, filename: str = None, prefix: str = None, folder: str = None):

        if not filename:
            filename = self._screenshot_name(prefix)

        if not folder:
            path = os.path.abspath(tempfile.gettempdir())
        else:
            path = os.path.abspath(folder)

        if not os.path.exists(path):
            os.makedirs(path)

        save = os.path.join(path, filename)

        log.info(f'Saving screenshot to: {save}')

        return self.browser.save_screenshot(save)

    @_isRunning
    def isRunning(self):
        return True

    def set_browser(self, browser: BrowserType):
        self.set_driver(driver=browser)

    def set_driver(self, driver: BrowserType):
        if driver:
            self.driver = driver

    @_isRunning
    def set_resolution(self, width=1920, height=1080, device_type=None):

        if device_type == 'pixel3':
            width = 1080
            height = 2160

        if device_type == 'web-small' or device_type == '800x600':
            width = 800
            height = 600

        if device_type == 'web-small-2' or device_type == '1024x768':
            width = 1024
            height = 768

        if device_type == 'web-small-3' or device_type == '1280x960':
            width = 1280
            height = 960

        if device_type == 'web-small-4' or device_type == '1280x1024':
            width = 1280
            height = 1024

        if device_type == 'web' or device_type == '1920x1080':
            width = 1920
            height = 1080

        if device_type == 'web-2' or device_type == '1600x1200':
            width = 1600
            height = 1200

        if device_type == 'web-3' or device_type == '1920x1200':
            width = 1920
            height = 1200

        if device_type == 'web-large' or device_type == '2560x1400':
            width = 2560
            height = 1400

        if device_type == 'web-long' or device_type == '1920x3080':
            width = 1920
            height = 3080

        if not width and not height:
            width = 1920
            height = 1080

        self.window_size = width, height
        self.browser.set_window_size(width, height)

    @_isRunning
    def quit(self):
        self.browser.close()
        self.browser.quit()
        self.browser.stop_client()
