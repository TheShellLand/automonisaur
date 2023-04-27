import os
import tempfile
import functools
import selenium

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from automon.log import Logging
from automon.helpers.dates import Dates
from automon.helpers.sleeper import Sleeper
from automon.helpers.sanitation import Sanitation

from .config import SeleniumConfig
from .browser_types import SeleniumBrowserType
from .user_agents import SeleniumUserAgentBuilder

log = Logging(name='SeleniumBrowser', level=Logging.DEBUG)


class SeleniumBrowser(object):
    config: SeleniumConfig
    type: SeleniumBrowserType

    def __init__(self, config: SeleniumConfig = None):
        """A selenium wrapper"""

        self.config = config or SeleniumConfig()
        self.driver = 'not set' or self.type.chrome_headless()
        self.status = ''

    def __repr__(self):
        if self.url:
            return f'{self.browser.name} {self.status} {self.browser.current_url} {self.window_size}'
        return f'{self.browser.name} {self.window_size}'

    @property
    def config_browser(self):
        return self.config

    @property
    def browser(self):
        """alias to selenium driver"""
        return self.driver

    @property
    def by(self) -> By:
        """Set of supported locator strategies"""
        return selenium.webdriver.common.by.By()

    @property
    def get_log(self, log_type: str = 'browser') -> list:
        """Gets the log for a given log type"""
        return self.browser.get_log(log_type)

    @property
    def keys(self):
        """Set of special keys codes"""
        return selenium.webdriver.common.keys.Keys

    @property
    def type(self):
        return SeleniumBrowserType(self.config)

    @property
    def url(self):
        if self.browser.current_url == 'data:,':
            return ''
        return self.browser.current_url

    @property
    def window_size(self):
        return self.config.window_size

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
            self.browser.get(url, **kwargs)
            self.status = 'OK'

            msg = f'GET {self.status} {self.browser.current_url}'
            if kwargs:
                msg += f', {kwargs}'
            log.debug(msg)
            return True
        except Exception as e:
            self.status = f'ERROR {url}'
            msg = f'GET {self.status}: {e}'
            log.error(msg, enable_traceback=False)

        return False

    @_is_running
    def get_page(self, *args, **kwargs):
        """alias to get"""
        return self.get(*args, **kwargs)

    @_is_running
    def get_page_source(self) -> str:
        """get page source"""
        return self.driver.page_source

    @_is_running
    def get_page_source_beautifulsoup(self, markdup: str = None, features: str = 'lxml') -> BeautifulSoup:
        """read page source with beautifulsoup"""
        if not markdup:
            markdup = self.get_page_source()
        return BeautifulSoup(markup=markdup, features=features)

    def get_random_user_agent(self, filter: list or str = None, case_sensitive: bool = False) -> list:
        return SeleniumUserAgentBuilder().get_random(filter=filter, case_sensitive=case_sensitive)

    @_is_running
    def get_screenshot_as_png(self, **kwargs):
        """screenshot as png"""
        return self.browser.get_screenshot_as_png(**kwargs)

    @_is_running
    def get_screenshot_as_base64(self, **kwargs):
        """screenshot as base64"""
        return self.browser.get_screenshot_as_base64(**kwargs)

    @_is_running
    def get_user_agent(self):
        return self.browser.execute_script("return navigator.userAgent")

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

    def set_browser(self, browser: SeleniumBrowserType) -> True:
        """set browser driver"""
        return self.set_driver(driver=browser)

    def set_driver(self, driver: SeleniumBrowserType) -> True:
        """set driver

        setting driver will launch browser
        """
        if driver:
            self.driver = driver
            log.info(f'Launching {self.browser.name}')
        return True

    @_is_running
    def set_window_size(self, width=1920, height=1080, device_type=None) -> bool:
        """set browser resolution"""

        self.config_browser.set_window_size(width=width, height=height, device_type=device_type)

        try:
            self.browser.set_window_size(self.config.window_size)
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
