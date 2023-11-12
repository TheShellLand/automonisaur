import os
import json
import base64
import datetime
import tempfile
import functools
import selenium
import selenium.webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from automon.log import logger
from automon.helpers.dates import Dates
from automon.helpers.sleeper import Sleeper
from automon.helpers.sanitation import Sanitation
from automon.integrations.requestsWrapper import RequestsClient

from .config import SeleniumConfig
from .browser_types import SeleniumBrowserType
from .user_agents import SeleniumUserAgentBuilder

log = logger.logging.getLogger(__name__)
log.setLevel(logger.DEBUG)


class SeleniumBrowser(object):
    config: SeleniumConfig
    webdriver: selenium.webdriver
    status: int

    def __init__(self, config: SeleniumConfig = None):
        """A selenium wrapper"""

        self._config = config or SeleniumConfig()
        self.request = None

    def __repr__(self):
        try:
            return str(dict(
                webdriver=self.webdriver.name or None,
                request_status=self.request_status,
                window_size=self.window_size,
            ))
        except Exception as error:
            pass

        return f'{__class__}'

    @property
    def by(self) -> By:
        """Set of supported locator strategies"""
        return selenium.webdriver.common.by.By()

    @property
    def config(self):
        return self._config

    @property
    def _current_url(self):
        try:
            self.webdriver.current_url
            return self.webdriver.current_url
        except Exception as error:
            return

    @property
    def webdriver(self):
        return self.config.webdriver

    @property
    def get_log(self) -> list:
        """Gets the log for a given log type"""
        logs = []
        for log_type in self.webdriver.log_types:
            logs.append(
                {
                    log_type: self.webdriver.get_log(log_type)
                }
            )

        return logs

    @property
    def keys(self):
        """Set of special keys codes"""
        return selenium.webdriver.common.keys.Keys

    def refresh(self):
        self.webdriver.refresh()
        log.info(f'{True}')

    @property
    def request_status(self):
        if self.request is not None:
            try:
                return self.request.results.status_code
            except:
                pass

    # @property
    # def type(self) -> SeleniumBrowserType:
    #     return SeleniumBrowserType(self.config)

    @property
    def url(self):
        if self.webdriver:
            log.info(str(dict(
                current_url=self._current_url
            )))
            if self._current_url == 'data:,':
                return ''
            return self._current_url

        log.info(str(dict(
            current_url=None
        )))
        return ''

    @property
    def window_size(self):
        return self.config.set_webdriver().window_size

    def _screenshot_name(self, prefix=None):
        """Generate a unique filename"""

        title = self.webdriver.title
        url = self._current_url
        hostname = urlparse(url).hostname

        hostname_ = Sanitation.ascii_numeric_only(hostname)
        title_ = Sanitation.ascii_numeric_only(title)
        timestamp = Dates.filename_timestamp()

        if prefix:
            prefix = Sanitation.safe_string(prefix)
            return f'{prefix}_{hostname_}_{title_}_{timestamp}.png'

        return f'{hostname_}_{title_}_{timestamp}.png'

    def action_click(self, xpath: str, note: str = None) -> str or False:
        """perform mouse command"""
        try:
            click = self.find_element(value=xpath, by=self.by.XPATH)
            click.click()
            if note:
                log.debug(str(dict(
                    note=note,
                    xpath=xpath,
                )))
            else:
                log.debug(str(dict(
                    xpath=xpath,
                )))
            return click

        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            log.error(str(dict(
                url=self.url,
                xpath=xpath,
                message=message,
                session=session,
                stacktrace=stacktrace,
            )))
        return False

    def action_type(self, key: str or Keys, secret: bool = True):
        """perform keyboard command"""
        try:
            actions = selenium.webdriver.common.action_chains.ActionChains(
                self.webdriver)
            actions.send_keys(key)
            actions.perform()

            if secret:
                key = f'*' * len(key)

            log.debug(str(dict(
                send_keys=key,
            )))
            return True

        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            log.error(str(dict(
                url=self.url,
                send_keys=key,
                message=message,
                session=session,
                stacktrace=stacktrace,
            )))
        return False

    def add_cookie(self, cookie_dict: dict) -> bool:
        result = self.webdriver.add_cookie(cookie_dict=cookie_dict)

        if result is None:
            log.debug(f'{True}')
            return True

        log.error(f'{False}')
        return False

    def add_cookies(self, cookies_list: list):
        for cookie in cookies_list:
            self.add_cookie(cookie_dict=cookie)
            self.get_cookies_summary()

        log.debug(f'{True}')
        return True

    def add_cookie_from_file(self, file: str = None) -> bool:
        if not file and self.config.cookies_file:
            file = self.config.cookies_file
        else:
            file = 'cookies.txt'

        if os.path.exists(file):
            log.debug(f'{file}')
            with open(file, 'r') as cookies_file:
                self.add_cookies(
                    json.loads(cookies_file.read())
                )
            return True
        else:
            log.error(f'{file}')

        return False

    def add_cookie_from_base64(self, base64_str: str = None):
        if not base64_str and self.config.cookies_base64:
            base64_str = self.config.cookies_base64

        if base64_str:
            self.add_cookies(
                json.loads(base64.b64decode(base64_str))
            )
            log.debug(f'{True}')
            return True

        log.error(f'{False}')
        return False

    def delete_all_cookies(self) -> None:
        result = self.webdriver.delete_all_cookies()
        log.info(f'{True}')
        return result

    def get_cookie(self, name: str) -> dict:
        result = self.webdriver.get_cookie(name=name)
        log.info(f'{result}')
        return result

    def get_cookies(self) -> [dict]:
        result = self.webdriver.get_cookies()
        log.debug(f'{True}')
        return result

    def get_cookies_base64(self) -> base64:
        result = self.get_cookies()
        log.debug(f'{True}')
        return base64.b64encode(
            json.dumps(result).encode()
        ).decode()

    def get_cookies_summary(self):
        result = self.get_cookies()
        summary = {}
        if result:
            for cookie in result:
                cookie = dict(cookie)
                domain = cookie.get('domain')
                name = cookie.get('name')
                expiry = cookie.get('expiry')

                if domain in summary.keys():
                    if expiry:
                        summary[domain].append({
                            f'{name}': f'{datetime.datetime.fromtimestamp(expiry)}'
                        })
                    else:
                        summary[domain].append(name)
                else:
                    summary[domain] = [name]

        log.debug(f'{summary}')
        return summary

    def close(self):
        """close browser"""
        log.info(f'closed')
        self.webdriver.close()

    @staticmethod
    def error_parsing(error) -> tuple:
        error_parsed = f'{error}'.splitlines()
        error_parsed = [f'{x}'.strip() for x in error_parsed]
        message = error_parsed[0]
        session = error_parsed[1]
        stacktrace = error_parsed[2:]
        stacktrace = ' '.join(stacktrace)

        return message, session, stacktrace

    def find_element(
            self,
            value: str,
            by: By.ID = By.ID,
            **kwargs):
        """find element"""
        element = self.webdriver.find_element(value=value, by=by, **kwargs)
        log.info(str(dict(
            url=self.url,
            text=element.text,
            value=value,
        )))
        return element

    def find_xpath(self, value: str, by: By = By.XPATH, **kwargs):
        """find xpath"""
        xpath = self.find_element(value=value, by=by, **kwargs)
        log.info(str(dict(
            url=self.url,
            text=xpath.text,
            value=value,
        )))
        return xpath

    def get(self, url: str, **kwargs) -> bool:
        """get url"""
        try:
            if self.webdriver.get(url, **kwargs) is None:
                self.request = RequestsClient(url=url)

                log.info(str(dict(
                    url=url,
                    current_url=self._current_url,
                    request_status=self.request_status,
                    kwargs=kwargs
                )))
            return True
        except Exception as error:
            self.request = RequestsClient(url=url)
            log.error(str(dict(
                error=error,
                request_status=self.request_status
            )))

        return False

    def get_page(self, *args, **kwargs):
        """alias to get"""
        return self.get(*args, **kwargs)

    def get_page_source(self) -> str:
        """get page source"""
        return self.webdriver.page_source

    def get_page_source_beautifulsoup(self, markdup: str = None, features: str = 'lxml') -> BeautifulSoup:
        """read page source with beautifulsoup"""
        if not markdup:
            markdup = self.get_page_source()
        return BeautifulSoup(markup=markdup, features=features)

    def get_random_user_agent(self, filter: list or str = None, case_sensitive: bool = False) -> list:
        return SeleniumUserAgentBuilder().get_random(filter=filter, case_sensitive=case_sensitive)

    def get_screenshot_as_base64(self, **kwargs):
        """screenshot as base64"""
        screenshot = self.webdriver.get_screenshot_as_base64(**kwargs)
        log.debug(f'{round(len(screenshot) / 1024)} KB')

        return screenshot

    def get_screenshot_as_file(
            self,
            filename: str = None,
            prefix: str = None,
            folder: str = None,
            **kwargs
    ) -> bool:
        return self.save_screenshot(
            self,
            filename=filename,
            prefix=prefix,
            folder=folder,
            **kwargs
        )

    def get_screenshot_as_png(self, **kwargs):
        """screenshot as png"""
        screenshot = self.webdriver.get_screenshot_as_png(**kwargs)
        log.debug(f'{round(len(screenshot) / 1024)} KB')

        return screenshot

    def get_user_agent(self):
        return self.webdriver.execute_script("return navigator.userAgent")

    def is_running(self) -> bool:
        """browser is running"""
        if self.webdriver:
            log.info(f'{True}')
            return True
        log.error(f'{False}')
        return False

    def quit(self) -> bool:
        """gracefully quit browser"""
        try:
            self.webdriver.close()
            self.webdriver.quit()
            self.webdriver.stop_client()
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            log.error(str(dict(
                message=message,
                session=session,
                stacktrace=stacktrace,
            )))
            return False
        return True

    def save_cookies_to_file(self, file: str = 'cookies.txt'):
        with open(file, 'w') as cookies:
            cookies.write(
                json.dumps(self.get_cookies())
            )

        if os.path.exists(file):
            log.info(f'{os.path.abspath(file)} ({os.stat(file).st_size} B)')
            return True

        log.error(f'{file}')
        return False

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

        if self.webdriver.save_screenshot(save, **kwargs):
            log.info(f'Saving screenshot to: {save} ({round(os.stat(save).st_size / 1024)} KB)')
            return True

        return False

    def set_webdriver(self):
        return self.config

    def set_window_size(self, width=1920, height=1080, device_type=None) -> bool:
        """set browser resolution"""

        try:
            self.config.set_webdriver().webdriver_wrapper.set_window_size(width=width, height=height,
                                                                          device_type=device_type)
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            log.error(str(dict(
                message=message,
                session=session,
                stacktrace=stacktrace,
            )))
            return False
        return True

    def set_window_position(self, x: int = 0, y: int = 0):
        """set browser position"""
        result = self.webdriver.set_window_position(x, y)
        log.info(f'{result}')
        return result

    def run(self):
        """run browser"""
        return self.config.run()

    def start(self):
        """alias to run"""
        return self.run()

    def wait_for(
            self,
            value: str or list,
            by: By = By.XPATH,
            retries: int = 5,
            fail_on_error: bool = True,
            **kwargs) -> str or False:
        """wait for something"""
        if not retries:
            retries = 5

        retry = 0
        while True:
            try:
                if isinstance(value, list):
                    values = value
                    for value in values:
                        try:
                            self.find_element(
                                by=by,
                                value=value,
                                **kwargs)
                            log.debug(str(dict(
                                by=by,
                                url=self.url,
                                value=value,
                            )))
                            return value
                        except:
                            log.error(str(dict(
                                by=by,
                                url=self.url,
                                value=value,
                            )))
                else:
                    self.find_element(
                        by=by,
                        value=value,
                        **kwargs)
                    log.debug(str(dict(
                        by=by,
                        url=self.url,
                        value=value,
                    )))
                    return value
            except Exception as error:
                log.error(str(dict(
                    by=by,
                    url=self.url,
                    value=value,
                    error=error,
                )))
                Sleeper.seconds(0.2)

            retry += 1

            log.error(str(dict(
                url=self.url,
                retry=f'{retry}/{retries}',
            )))

            if retry == retries:
                break

        if fail_on_error:
            raise Exception(str(dict(
                by=by,
                url=self.url,
                value=value,
            )))

        return False

    def wait_for_element(
            self,
            element: str or list,
            retries: int = None,
            fail_on_error: bool = True,
            **kwargs
    ) -> str or False:
        """wait for an element"""
        return self.wait_for(
            value=element,
            by=self.by.ID,
            retries=retries,
            fail_on_error=fail_on_error,
            **kwargs
        )

    def wait_for_xpath(
            self,
            xpath: str or list,
            retries: int = None,
            fail_on_error: bool = True,
            **kwargs
    ) -> str or False:
        """wait for an xpath"""
        return self.wait_for(
            value=xpath,
            by=self.by.XPATH,
            retries=retries,
            fail_on_error=fail_on_error,
            **kwargs
        )
