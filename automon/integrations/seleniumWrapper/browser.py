import os
import tempfile
import functools
import selenium

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from urllib.parse import urlparse

from automon.log import Logging
from automon.helpers.dates import Dates
from automon.helpers.sleeper import Sleeper
from automon.helpers.sanitation import Sanitation

from .config import SeleniumConfig
from .browser_types import BrowserType

log = Logging(name='SeleniumBrowser', level=Logging.DEBUG)


class SeleniumBrowser(object):
    config: SeleniumConfig
    type: BrowserType

    def __init__(self, config: SeleniumConfig = None):
        self.config = config or SeleniumConfig()
        self.type = self._browser_type = BrowserType(self.config)
        self.driver = 'not set' or self.type.chrome_headless
        self.window_size = ''

        self.url = ''
        self.status = ''

    def __repr__(self):
        if self.url:
            return f'{self.browser.name} {self.status} {self.url} {self.window_size}'
        return f'{self.browser}'

    @property
    def browser(self):
        return self.driver

    @property
    def by(self) -> By:
        return selenium.webdriver.common.by.By

    @property
    def keys(self):
        return selenium.webdriver.common.keys.Keys()

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
    def action_click(self, xpath: str) -> str or False:
        """perform mouse command"""
        try:
            click = self.find_element(value=xpath, by=self.by.XPATH)
            click.click()
            log.debug(f'click: {xpath}')
            return click
        except Exception as e:
            log.error(f'failed to click: {xpath}, {e}', enable_traceback=False)
        return False

    @_isRunning
    def action_type(self, key: str or Keys):
        """perform keyboard command"""
        try:
            log.debug(f'type: {key}')
            actions = selenium.webdriver.common.action_chains.ActionChains(
                self.browser)
            actions.send_keys(key)
            actions.perform()
            return True
        except Exception as e:
            log.error(f'failed to type: {key}, {e}', enable_traceback=False)
        return False

    @_isRunning
    def close(self):
        log.info(f'Browser closed')
        self.browser.close()

    @_isRunning
    def find_element(
            self,
            value: str,
            by: By = By.ID,
            **kwargs):
        """find element"""
        return self.browser.find_element(value=value, by=by, **kwargs)

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
    def isRunning(self):
        return True

    @_isRunning
    def quit(self):
        self.browser.close()
        self.browser.quit()
        self.browser.stop_client()

    @_isRunning
    def save_screenshot(
            self,
            filename: str = None,
            prefix: str = None,
            folder: str = None):

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

    def wait_for_generic(self, value: str, by: By = By.XPATH):
        while True:
            try:
                self.browser.find_element(by=by, value=value)
                break
            except Exception as error:
                log.error(f'waiting for {by}: {value}, {error}',
                          enable_traceback=False)
                Sleeper.seconds(f'wait_for_xpath', 1)
        return True

    def wait_for_element(self, element: str) -> bool:
        while True:
            try:
                self.browser.find_element(by=self.by.ID, value=element)
                break
            except Exception as error:
                log.error(f'waiting for element: {element}, {error}',
                          enable_traceback=False)
                Sleeper.seconds(f'wait_for_xpath', 1)
        return True

    def wait_for_xpath(self, xpath: str) -> bool:
        while True:
            try:
                self.browser.find_element(by=self.by.XPATH, value=xpath)
                break
            except Exception as error:
                log.error(f'waiting for xpath: {xpath}, {error}',
                          enable_traceback=False)
                Sleeper.seconds(f'wait_for_xpath', 1)
        return True
