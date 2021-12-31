import os

import tempfile

from urllib.parse import urlparse

from automon.log import Logging
from automon.helpers.dates import Dates
from automon.helpers.sleeper import Sleeper
from automon.helpers.sanitation import Sanitation
from automon.integrations.selenium.config import SeleniumConfig


class SeleniumBrowser:

    def __init__(self, config: SeleniumConfig = None):
        self._log = Logging(name=SeleniumBrowser.__name__, level=Logging.DEBUG)

        self.config = config or SeleniumConfig()
        self.webdriver = self.config.webdriver
        self.connected = False

        try:
            self.browser = self.webdriver.Chrome()
            self.connected = True
        except Exception as e:
            self._log.error(f'Unable to spawn browser: {e}')

    def get(self, url: str):
        try:
            self.browser.get(url)
            return True
        except Exception as e:
            self._log.error(f'Error getting {url}: {e}')

        return False

    def get_screenshot_as_png(self):
        return self.browser.get_screenshot_as_png()

    def get_screenshot_as_base64(self):
        return self.browser.get_screenshot_as_base64()

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

        self._log.info(f'Saving screenshot to: {save}')

        return self.browser.save_screenshot(save)

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

    def new_resolution(self, width=1920, height=1080, device_type='web'):

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

        self.browser.set_window_size(width, height)

    def close(self):
        self.browser.close()

    def quit(self):
        self.browser.close()
        self.browser.quit()
        self.browser.stop_client()


if __name__ == "__main__":
    pass
