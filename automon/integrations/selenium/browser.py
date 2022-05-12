import os
import tempfile
import functools

from urllib.parse import urlparse

from automon.log import Logging
from automon.helpers.dates import Dates
from automon.helpers.sleeper import Sleeper
from automon.helpers.sanitation import Sanitation

from .config import SeleniumConfig

log = Logging(name='SeleniumBrowser', level=Logging.DEBUG)


class SeleniumBrowser(object):

    def __init__(self, config: SeleniumConfig = None):
        self.config = config or SeleniumConfig()
        self.webdriver = self.config.webdriver
        self.browser = None

    def _isRunning(func):
        @functools.wraps(func)
        def wrapped(self, *args, **kwargs):
            if self.browser:
                return func(self, *args, **kwargs)
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
    def isRunning(self):
        return True

    def chrome(self):
        return self.webdriver.Chrome()

    def chromium_edge(self):
        return self.webdriver.ChromiumEdge()

    def edge(self):
        return self.webdriver.Edge()

    def firefox(self):
        return self.webdriver.Firefox()

    def ie(self):
        return self.webdriver.Ie()

    def opera(self):
        return self.webdriver.Opera()

    def proxy(self):
        return self.webdriver.Proxy()

    def remote(self):
        return self.webdriver.Remote()

    def safari(self):
        return self.webdriver.Safari()

    def webkit_gtk(self):
        return self.webdriver.WebKitGTK()

    def wpewebkit(self):
        return self.webdriver.WPEWebKit()

    def close(self):
        self.browser.close()

    @_isRunning
    def get(self, url: str):
        try:
            self.browser.get(url)
            return True
        except Exception as e:
            log.error(f'Error getting {url}: {e}')

        return False

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

        self.browser.set_window_size(width, height)

    @_isRunning
    def quit(self):
        self.browser.close()
        self.browser.quit()
        self.browser.stop_client()
