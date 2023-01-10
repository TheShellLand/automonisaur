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
        """A selenium wrapper"""

        self.config = config or SeleniumConfig()
        self.driver = 'not set' or self.type.chrome_headless
        self.window_size = ''

        self.url = ''
        self.status = ''

    def __repr__(self):
        if self.url:
            return f'{self.browser.name} {self.status} {self.url} {self.window_size}'
        return f'{self.browser}'

    @property
    def type(self):
        return BrowserType(self.config)

    @property
    def browser(self):
        """alias to selenium driver"""
        return self.driver

    @property
    def by(self) -> By:
        """Set of supported locator strategies"""
        return selenium.webdriver.common.by.By()

    @property
    def keys(self):
        """Set of special keys codes"""
        return selenium.webdriver.common.keys.Keys

    @property
    def get_log(self, log_type: str = 'browser') -> list:
        """Gets the log for a given log type"""
        return self.browser.get_log(log_type)

    def _is_running(func) -> functools.wraps:
        @functools.wraps(func)
        def wrapped(self, *args, **kwargs):
            if self.browser != 'not set':
                return func(self, *args, **kwargs)
            log.error(f'Browser is not set!', enable_traceback=False)
            return False

        return wrapped

    def _screenshot_name(self, prefix=None):
        """Generate a unique filename"""

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

    @_is_running
    def action_click(self, xpath: str, note: str = None) -> str or False:
        """perform mouse command"""
        try:
            click = self.find_element(value=xpath, by=self.by.XPATH)
            click.click()
            if note:
                log.debug(f'click: ({note}) {xpath}')
            else:
                log.debug(f'click: {xpath}')
            return click
        except Exception as e:
            log.error(f'failed to click: {xpath}, {e}', enable_traceback=False)
        return False

    @_is_running
    def action_type(self, key: str or Keys, secret: bool = False):
        """perform keyboard command"""
        try:
            actions = selenium.webdriver.common.action_chains.ActionChains(
                self.browser)
            actions.send_keys(key)
            actions.perform()

            if secret:
                key = f'*' * len(key)

            log.debug(f'type: {key}')
            return True
        except Exception as e:
            log.error(f'failed to type: {key}, {e}', enable_traceback=False)
        return False

    @_is_running
    def close(self):
        """close browser"""
        log.info(f'Browser closed')
        self.browser.close()

    @_is_running
    def find_element(
            self,
            value: str,
            by: By = By.ID,
            **kwargs):
        """find element"""
        return self.browser.find_element(value=value, by=by, **kwargs)

    @_is_running
    def find_xpath(self, value: str, by: By = By.XPATH, **kwargs):
        """find xpath"""
        return self.find_element(value=value, by=by, **kwargs)

    @_is_running
    def get(self, url: str, **kwargs) -> bool:
        """get url"""
        try:
            self.url = url
            self.browser.get(url, **kwargs)
            self.status = 'OK'
            log.debug(f'GET {url}, {kwargs}')
            return True
        except Exception as e:
            self.status = 'ERROR'
            log.error(f'Error getting {url}: {e}', enable_traceback=False)

        return False

    @_is_running
    def get_page(self, *args, **kwargs):
        """alias to get"""
        return self.get(*args, **kwargs)

    @_is_running
    def get_screenshot_as_png(self, **kwargs):
        """screenshot as png"""
        return self.browser.get_screenshot_as_png(**kwargs)

    @_is_running
    def get_screenshot_as_base64(self, **kwargs):
        """screenshot as base64"""
        return self.browser.get_screenshot_as_base64(**kwargs)

    @_is_running
    def is_running(self) -> bool:
        """browser is running"""
        return True

    @_is_running
    def quit(self) -> bool:
        """gracefully quit browser"""
        try:
            self.browser.close()
            self.browser.quit()
            self.browser.stop_client()
        except Exception as error:
            log.error(f'failed to quit browser. {error}')
            return False
        return True

    @_is_running
    def save_screenshot(
            self,
            filename: str = None,
            prefix: str = None,
            folder: str = None,
            **kwargs) -> bool:
        """save screenshot to file"""

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

        return self.browser.save_screenshot(save, **kwargs)

    def set_browser(self, browser: BrowserType) -> True:
        """set browser driver"""
        return self.set_driver(driver=browser)

    def set_driver(self, driver: BrowserType) -> True:
        """set driver"""
        if driver:
            self.driver = driver
        return True

    @_is_running
    def set_resolution(self, width=1920, height=1080, device_type=None) -> bool:
        """set browser resolution"""

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

        try:
            self.browser.set_window_size(width, height)
        except Exception as error:
            log.error(f'failed to set resolution. {error}')
            return False
        return True

    def wait_for(
            self,
            value: str or list,
            by: By = By.XPATH,
            retries: int = 30,
            **kwargs) -> str or False:
        """wait for something"""
        retry = 1
        while True:
            try:
                if isinstance(value, list):
                    for each in value:
                        self.find_element(
                            by=by,
                            value=each,
                            **kwargs)
                        value = each
                        log.debug(f'found {by}: {value}')
                        return value
                else:
                    self.find_element(
                        by=by,
                        value=value,
                        **kwargs)
                    log.debug(f'found {by}: {value}')
                    return value
            except Exception as error:
                log.error(f'waiting for {by}: {value}, {error}',
                          enable_traceback=False)
                Sleeper.seconds(f'wait for', round(retry / 2))

            retry += 1

            if retry > retries:
                log.error(f'max wait reached', enable_traceback=False)
                break
        return False

    def wait_for_element(self, element: str or list, **kwargs) -> str or False:
        """wait for an element"""
        return self.wait_for(value=element, by=self.by.ID, **kwargs)

    def wait_for_xpath(self, xpath: str or list, **kwargs) -> str or False:
        """wait for an xpath"""
        return self.wait_for(value=xpath, by=self.by.XPATH, **kwargs)
