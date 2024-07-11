import os
import json
import time
import base64
import datetime
import tempfile
import selenium
import selenium.webdriver
import selenium.webdriver.common.by
import selenium.webdriver.remote.webelement

from selenium.webdriver.common.keys import Keys
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from automon import log
from automon.helpers.dates import Dates
from automon.helpers.sleeper import Sleeper
from automon.helpers.sanitation import Sanitation

from .config import SeleniumConfig
from .user_agents import SeleniumUserAgentBuilder
from .exceptions import *

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


class SeleniumBrowser(object):
    config: SeleniumConfig
    webdriver: selenium.webdriver
    status: int

    def __init__(self, config: SeleniumConfig = None):
        """A selenium wrapper"""

        self._config = config or SeleniumConfig()
        self._selenium = selenium

        self.logs = {}

    def __repr__(self):
        try:
            return str(dict(
                webdriver=self.webdriver.name or None,
                window_size=self.window_size,
            ))
        except Exception as error:
            pass

        return f'{__class__}'

    @property
    def by(self) -> selenium.webdriver.common.by.By:
        """Set of supported locator strategies"""
        return selenium.webdriver.common.by.By()

    @property
    def config(self):
        return self._config

    async def cookie_file_to_dict(self, file: str = 'cookies.json') -> list:
        logger.debug(dict(
            cookie_file_to_dict=file
        ))
        with open(file, 'r') as file:
            return json.loads(file.read())

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

    async def get_log(self, log_type: str) -> list:
        """Get logs for log type"""
        return self.webdriver.get_log(log_type)

    async def get_logs(self) -> dict:
        """Get all logs

        you can only run this once
        afterwards the logs are cleared from the webdriver
        """
        for log_type in self.webdriver.log_types:
            self.logs.update(
                {
                    log_type: self.webdriver.get_log(log_type)
                }
            )
        return self.logs

    async def get_log_browser(self) -> list:
        """Get browser logs"""
        logs = await self.get_log('browser')
        return logs

    async def get_log_driver(self) -> list:
        """Get driver logs"""
        logs = await self.get_log('driver')
        return logs

    async def get_log_performance(self) -> list:
        """Get performance logs"""
        logs = await self.get_log('performance')
        return logs

    async def check_page_load_finished(self) -> bool:
        """Checks for `frameStoppedLoading` string in performance logs"""
        logs = await self.get_log_performance()

        check = []
        for log_dict in logs:
            if 'frameStoppedLoading' in log_dict.get('message'):
                check.append(log_dict)

        if check:
            return True

        return False

    @property
    def keys(self):
        """Set of special keys codes"""
        return selenium.webdriver.common.keys.Keys

    async def refresh(self) -> None:
        self.webdriver.refresh()
        logger.info(dict(
            refresh_page=self.current_url
        ))

    @property
    def url(self):
        return self.current_url

    @property
    def user_agent(self):
        try:
            return self.webdriver.execute_script("return navigator.userAgent")
        except:
            return None

    @property
    def current_url(self):
        if self.webdriver:
            if self._current_url == 'data:,':
                return ''
            return self._current_url

        logger.info(None)
        return ''

    @property
    def window_size(self):
        return self.config.webdriver_wrapper.window_size

    def _screenshot_name(self, prefix=None):
        """Generate a unique filename"""

        title = self.webdriver.title
        url = self.current_url
        hostname = urlparse(url).hostname

        hostname_ = Sanitation.ascii_numeric_only(hostname)
        title_ = Sanitation.ascii_numeric_only(title)
        timestamp = Dates.filename_timestamp()

        if prefix:
            prefix = Sanitation.safe_string(prefix)
            return f'{prefix}_{hostname_}_{title_}_{timestamp}.png'

        return f'{hostname_}_{title_}_{timestamp}.png'

    async def action_click(
            self,
            element: selenium.webdriver.remote.webelement.WebElement, **kwargs):
        """perform mouse click"""
        try:
            logger.debug(dict(
                tag_name=element.tag_name,
                text=element.text,
                accessible_name=element.accessible_name,
                aria_role=element.aria_role))
            return element.click(**kwargs)

        except Exception as error:
            raise Exception(error)

    async def action_type(
            self,
            key: str or Keys,
            secret: bool = False) -> selenium.webdriver.common.action_chains.ActionChains:
        """perform keyboard command"""

        if secret:
            logger.debug(dict(send_keys=f'*' * len(f'{key}')))
        else:
            logger.debug(dict(send_keys=key))

        try:
            return selenium.webdriver.common.action_chains.ActionChains(
                self.webdriver).send_keys(key).perform()

        except Exception as error:
            raise Exception(error)

    async def action_type_up(
            self,
            key: str or Keys,
            secret: bool = False) -> selenium.webdriver.common.action_chains.ActionChains:
        """release key"""

        if secret:
            logger.debug(dict(send_keys=f'*' * len(f'{key}')))
        else:
            logger.debug(dict(send_keys=key))

        try:
            return selenium.webdriver.common.action_chains.ActionChains(
                self.webdriver).key_up(key).perform()

        except Exception as error:
            raise Exception(error)

    async def action_type_down(
            self,
            key: str or Keys,
            secret: bool = False, ) -> selenium.webdriver.common.action_chains.ActionChains:
        """hold key down"""

        if secret:
            logger.debug(dict(send_keys=f'*' * len(f'{key}')))
        else:
            logger.debug(dict(send_keys=key))

        try:
            return selenium.webdriver.common.action_chains.ActionChains(
                self.webdriver).key_down(key).perform()

        except Exception as error:
            raise Exception(error)

    async def add_cookie(self, cookie_dict: dict) -> bool:
        result = self.webdriver.add_cookie(cookie_dict=cookie_dict)

        if result is None:
            logger.debug(dict(
                domain=cookie_dict.get('domain'),
                path=cookie_dict.get('path'),
                secure=cookie_dict.get('secure'),
                expiry=cookie_dict.get('expiry'),
                name=cookie_dict.get('name'),
            ))
            return True

        logger.error(dict(
            add_cookie=cookie_dict
        ))
        return False

    async def add_cookie_from_file(self, file: str) -> bool:
        """add cookies from file"""
        if os.path.exists(file):
            await self.add_cookies_from_list(
                await self.cookie_file_to_dict(file=file)
            )
            return True

        logger.error(f'{file}')
        return False

    async def add_cookies_from_list(self, cookies_list: list) -> bool:
        for cookie in cookies_list:
            await self.add_cookie(cookie_dict=cookie)

        logger.debug(dict(
            add_cookies_from_list=len(cookies_list)
        ))
        return True

    async def add_cookie_from_current_url(self):
        logger.info(f'{self.url}')
        return self.add_cookie_from_url(self.url)

    async def add_cookie_from_url(self, url: str) -> bool:
        """add cookies from matching hostname"""
        cookie_file = await self._url_filename(url=url)

        if os.path.exists(cookie_file):
            logger.info(f'{cookie_file}')
            return await self.add_cookie_from_file(file=cookie_file)

        logger.error(f'{cookie_file}')

    async def add_cookie_from_base64(self, base64_str: str) -> bool:
        if base64_str:
            await self.add_cookies_from_list(
                json.loads(base64.b64decode(base64_str))
            )
            logger.debug(f'{True}')
            return True

        logger.error(f'{base64_str}')
        return False

    async def autosave_cookies(self) -> bool:
        if self.current_url:
            await self.load_cookies_for_current_url()
            await self.refresh()
            await self.save_cookies_for_current_url()
            return True

    async def delete_all_cookies(self) -> None:
        result = self.webdriver.delete_all_cookies()
        logger.info(f'{True}')
        return result

    async def _url_filename(self, url: str):
        parsed = await self.urlparse(url)
        hostname = parsed.hostname
        cookie_file = f'cookies-{hostname}.json'
        logger.debug(dict(
            _url_filename=cookie_file
        ))
        return cookie_file

    async def get_cookie(self, name: str) -> dict:
        result = self.webdriver.get_cookie(name=name)
        logger.info(f'{result}')
        return result

    async def get_cookies(self) -> [dict]:
        cookies = self.webdriver.get_cookies()
        logger.debug(dict(
            get_cookies=len(cookies)
        ))
        return cookies

    async def get_cookies_base64(self) -> base64:
        cookies = await self.get_cookies()
        logger.debug(f'{True}')
        return base64.b64encode(
            json.dumps(cookies).encode()
        ).decode()

    async def get_cookies_json(self) -> json.dumps:
        cookies = await self.get_cookies()
        logger.debug(dict(
            get_cookies_json=len(cookies)
        ))
        return json.dumps(cookies)

    async def get_cookies_summary(self):
        result = await self.get_cookies()
        summary = {}
        if result:
            for cookie in result:
                cookie = dict(cookie)
                domain = cookie.get('domain')
                name = cookie.get('name')
                expiry = cookie.get('expiry')

                if domain in summary.keys():
                    summary[domain].append(cookie)
                else:
                    summary[domain] = [cookie]

        logger.debug(f'{summary}')
        return summary

    async def close(self):
        """close browser"""
        logger.info(f'closed')
        self.webdriver.close()

    @staticmethod
    async def error_parsing(error) -> tuple:
        try:
            error_parsed = f'{error}'.splitlines()
            error_parsed = [f'{x}'.strip() for x in error_parsed]
            message = error_parsed[0]
            session = error_parsed[1]
            stacktrace = error_parsed[2:]
            stacktrace = ' '.join(stacktrace)

            return message, session, stacktrace

        except Exception as e:
            logger.error(dict(
                exception=e,
                error=error,
            ))

        return error, None, None

    async def find_anything(
            self,
            value: str,
            by: selenium.webdriver.common.by.By = None,
            case_sensitive: bool = False,
            contains: bool = True,
            return_first: bool = False,
            **kwargs) -> list:
        """fuzzy search through everything

        find all tags
        find all matches within meta data
        """
        logger.info(dict(
            current_url=self.current_url,
            value=value,
            by=by,
            case_sensitive=case_sensitive,
            contains=contains,
            kwargs=kwargs,
        ))

        by_types = [
            self.by.TAG_NAME,
            self.by.ID,
            self.by.NAME,
            self.by.CLASS_NAME,
            self.by.LINK_TEXT,
            self.by.PARTIAL_LINK_TEXT,
            self.by.CSS_SELECTOR,
            self.by.XPATH,
        ]

        if by:
            by_types = [by]

        MATCHED = []

        for by_ in by_types:
            elements = await self.find_elements(value='*', by=by_, **kwargs)
            for element in elements:
                dirs = dir(element)
                dir_meta = []
                for dir_ in dirs:
                    try:
                        dir_meta.append(
                            getattr(element, f'{dir_}')
                        )

                        MATCH = f'{value}'
                        AGAINST = f'''{getattr(element, f'{dir_}')}'''

                        if case_sensitive:
                            MATCH = f'{value}'.lower()
                            AGAINST = f'''{getattr(element, f'{dir_}')}'''.lower()

                    except:
                        pass

                    FOUND = None

                    if MATCH == AGAINST and not contains:
                        FOUND = element

                    if MATCH in AGAINST and contains:
                        FOUND = element

                    if FOUND and FOUND not in MATCHED:
                        logger.info(dict(
                            MATCH=MATCH,
                            AGAINST=AGAINST,
                            attribute=dir_,
                            element=element,
                        ))
                        MATCHED.append(FOUND)

                        if return_first:
                            return MATCHED
        return MATCHED

    async def find_element(
            self,
            value: str,
            by: selenium.webdriver.common.by.By,
            **kwargs) -> selenium.webdriver.Chrome.find_element:
        """find element"""
        logger.info(dict(
            current_url=self.current_url,
            value=value,
            by=by,
        ))
        return self.webdriver.find_element(value=value, by=by, **kwargs)

    async def find_elements(
            self,
            value: str,
            by: selenium.webdriver.common.by.By,
            **kwargs) -> list:
        """find elements"""
        logger.info(dict(
            current_url=self.current_url,
            value=value,
            by=by,
        ))
        return self.webdriver.find_elements(value=value, by=by, **kwargs)

    async def find_xpath(
            self,
            value: str,
            by: selenium.webdriver.common.by.By = selenium.webdriver.common.by.By.XPATH,
            **kwargs) -> selenium.webdriver.Chrome.find_element:
        """find xpath"""
        logger.info(dict(
            current_url=self.current_url,
            value=value,
            by=by,
        ))
        return await self.find_element(value=value, by=by, **kwargs)

    async def get(self, url: str, **kwargs) -> bool:
        """get url"""
        if not self.webdriver:
            logger.error(f'missing webdriver')
            raise Exception(f'missing webdriver')

        try:
            if self.webdriver.get(url, **kwargs) is None:
                logger.info(str(dict(
                    url=url,
                    current_url=self.current_url,
                    kwargs=kwargs
                )))

            if self.config.cookies_autosave:
                await self.autosave_cookies()

            return True
        except Exception as error:
            logger.error(dict(
                error=error,
            ))

        return False

    async def get_page(self, *args, **kwargs):
        """alias to get"""
        return self.get(*args, **kwargs)

    async def get_page_source(self) -> str:
        """get page source"""
        return self.webdriver.page_source

    async def get_page_source_beautifulsoup(
            self,
            markdup: str = None,
            features: str = 'lxml') -> BeautifulSoup:
        """read page source with beautifulsoup"""
        if not markdup:
            markdup = await self.get_page_source()
        return BeautifulSoup(
            markup=markdup,
            features=features)

    async def get_random_user_agent(
            self,
            filter: list or str = None,
            case_sensitive: bool = False) -> str:
        return SeleniumUserAgentBuilder().get_random_agent(
            filter=filter,
            case_sensitive=case_sensitive)

    async def get_screenshot_as_base64(self, **kwargs):
        """screenshot as base64"""
        screenshot = self.webdriver.get_screenshot_as_base64(**kwargs)
        logger.debug(f'{round(len(screenshot) / 1024)} KB')

        return screenshot

    async def get_screenshot_as_file(
            self,
            filename: str = None,
            prefix: str = None,
            folder: str = None,
            **kwargs) -> bool:
        return await self.save_screenshot(
            self,
            filename=filename,
            prefix=prefix,
            folder=folder,
            **kwargs)

    async def get_screenshot_as_png(self, **kwargs):
        """screenshot as png"""
        screenshot = self.webdriver.get_screenshot_as_png(**kwargs)
        logger.debug(f'{round(len(screenshot) / 1024)} KB')

        return screenshot

    async def is_running(self) -> bool:
        """browser is running"""
        if self.webdriver:
            logger.info(f'{True}')
            return True
        logger.error(f'{False}')
        return False

    async def load_cookies_for_current_url(self) -> bool:
        filename = await self._url_filename(url=self.url)
        logger.info(dict(
            load_cookies_for_current_url=filename,
            url=self.url,
        ))
        return await self.add_cookie_from_file(file=filename)

    @property
    def page_source(self):
        return self.webdriver.page_source

    async def urlparse(self, url: str):
        parsed = urlparse(url=url)
        logger.debug(dict(
            urlparse=parsed
        ))
        return parsed

    async def quit(self) -> bool:
        """gracefully quit browser"""
        try:
            self.webdriver.close()
            self.webdriver.quit()
            self.webdriver.stop_client()
        except Exception as error:
            message, session, stacktrace = await self.error_parsing(error)
            logger.error(str(dict(
                message=message,
                session=session,
                stacktrace=stacktrace,
            )))
            return False
        return True

    async def run(self):
        """run browser"""
        try:
            return await self.config.run()
        except Exception as error:
            logger.error(dict(
                error=error
            ))
            return False

    async def save_cookies_for_current_url(self) -> bool:
        filename = await self._url_filename(url=self.url)
        logger.info(dict(
            save_cookies_for_current_url=filename,
            url=self.url,
        ))
        return await self.save_cookies_to_file(file=filename)

    async def save_cookies_to_file(self, file: str) -> bool:
        with open(file, 'w') as cookies:
            cookies.write(
                await self.get_cookies_json()
            )

        if os.path.exists(file):
            logger.info(dict(
                save_cookies_to_file=os.path.abspath(file),
                bytes=os.stat(file).st_size
            ))
            return True

        logger.error(dict(
            file=file
        ))
        return False

    async def save_screenshot(
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
            logger.info(f'Saving screenshot to: {save} ({round(os.stat(save).st_size / 1024)} KB)')
            return True

        return False

    async def set_window_size(self, width=1920, height=1080, device_type=None) -> bool:
        """set browser resolution"""

        try:
            self.config.webdriver_wrapper.set_window_size(
                width=width,
                height=height,
                device_type=device_type)
        except Exception as error:
            message, session, stacktrace = await self.error_parsing(error)
            logger.error(str(dict(
                message=message,
                session=session,
                stacktrace=stacktrace,
            )))
            return False
        return True

    async def set_window_position(self, x: int = 0, y: int = 0):
        """set browser position"""
        result = self.webdriver.set_window_position(x, y)
        logger.info(f'{result}')
        return result

    async def start(self):
        """alias to run"""
        return await self.run()

    async def wait_for_anything(
            self,
            value: str,
            by: selenium.webdriver.common.by.By,
            case_sensitive: bool = False,
            contains: bool = True,
            timeout: int = 30,
            return_first: bool = False,
            **kwargs) -> list:
        """wait for anything"""
        timeout_start = time.time()
        timeout_elapsed = round(abs(timeout_start - time.time()), 1)

        while timeout_elapsed < timeout:

            logger.debug(str(dict(
                timeout=f'{timeout_elapsed}/{timeout}',
                current_url=self.current_url,
                value=value,
                by=by,
            )))

            try:
                find = await self.find_anything(
                    value=value,
                    by=by,
                    case_sensitive=case_sensitive,
                    contains=contains,
                    return_first=return_first,
                    **kwargs)

                if find:
                    return find

            except Exception as error:
                logger.error(error)

            timeout_elapsed = round(abs(timeout_start - time.time()), 1)

        raise ElementNotFoundException(value)

    async def wait_for_element(
            self,
            value: str,
            by: selenium.webdriver.common.by.By,
            timeout: int = 30,
            **kwargs) -> selenium.webdriver.Chrome.find_element:
        """wait for an element"""
        timeout_start = time.time()
        timeout_elapsed = round(abs(timeout_start - time.time()), 1)

        while timeout_elapsed < timeout:

            logger.debug(str(dict(
                timeout=f'{timeout_elapsed}/{timeout}',
                by=by,
                current_url=self.current_url,
                value=value,
            )))

            try:
                find = await self.find_element(
                    value=value,
                    by=by,
                    **kwargs)

                if find:
                    return find

            except Exception as error:
                logger.error(error)

            timeout_elapsed = round(abs(timeout_start - time.time()), 1)

        raise ElementNotFoundException(value)

    async def wait_for_elements(
            self,
            value: str,
            by: selenium.webdriver.common.by.By,
            timeout: int = 30,
            **kwargs) -> list:
        """wait for all matching elements"""
        timeout_start = time.time()
        timeout_elapsed = round(abs(timeout_start - time.time()), 1)

        while timeout_elapsed < timeout:

            logger.debug(str(dict(
                timeout=f'{timeout_elapsed}/{timeout}',
                by=by,
                current_url=self.current_url,
                value=value,
            )))

            try:
                find = await self.find_elements(
                    value=value,
                    by=by,
                    **kwargs)

                if find:
                    return find

            except Exception as error:
                logger.error(error)

            timeout_elapsed = round(abs(timeout_start - time.time()), 1)

        raise ElementNotFoundException(value)

    async def wait_for_id(
            self,
            value: str,
            timeout: int = 30,
            **kwargs) -> selenium.webdriver.Chrome.find_element:
        """wait for an element id"""
        return await self.wait_for_element(
            value=value,
            by=self.by.ID,
            timeout=timeout,
            **kwargs)

    async def wait_for_xpath(
            self,
            value: str,
            timeout: int = 30,
            **kwargs) -> selenium.webdriver.Chrome.find_element:
        """wait for a xpath"""
        return await self.wait_for_element(
            value=value,
            by=self.by.XPATH,
            timeout=timeout,
            **kwargs)
