import os
import re
import bs4
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

        self.autosaved = None

        self._logs = {}
        self.cache = {}

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

    def cookie_file_to_dict(self, file: str = 'cookies.json') -> list:
        """load cookie file as dict"""
        logger.debug(f'cookie_file_to_dict :: {file=}')
        with open(file, 'r') as file:
            logger.debug(f'cookie_file_to_dict :: read :: {file=}')
            logger.info(f'cookie_file_to_dict :: read :: done')
            return json.loads(file.read())

    @property
    def _current_url(self):
        """get browser current url"""
        try:
            return self.webdriver.current_url
        except Exception as error:
            return

    @property
    def logs(self):
        return self.get_logs()

    @property
    def webdriver(self):
        """get webdriver"""
        return self.config.webdriver

    def get_log(self, log_type: str) -> list:
        """Get logs for log type"""
        logger.debug(f'get_log :: {log_type=}')
        get_log = self.webdriver.get_log(log_type)
        logger.info(f'get_log :: done')
        return get_log

    def get_logs(self) -> dict:
        """Get all logs

        you can only run this once
        afterwards the logs are cleared from the webdriver
        """
        logger.debug(f'get_logs :: {len(self.webdriver.log_types)} types found :: {self.webdriver.log_types}')

        for log_type in self.webdriver.log_types:
            logs = self.webdriver.get_log(log_type)

            if log_type == 'performance':
                for x in logs:
                    x['message'] = json.loads(x['message'])

            if log_type in self._logs.keys():
                if logs:
                    self._logs[log_type].append(logs)
            else:
                self._logs[log_type] = logs

            logger.debug(f'get_logs :: {log_type} :: {len(self._logs[log_type])} logs')
            logger.info(f'get_logs :: {log_type} :: done')

        logger.debug(f'get_logs :: {len(self._logs)} total logs')
        logger.info(f'get_logs :: done')
        return self._logs

    def get_log_browser(self) -> list:
        """Get browser logs"""
        logger.debug(f'get_log_browser')
        logs = self.get_log('browser')
        logger.debug(f'get_log_browser :: {len(logs)} logs')
        logger.info(f'get_log_browser :: done')
        return logs

    def get_log_driver(self) -> list:
        """Get driver logs"""
        logger.debug(f'get_log_driver')
        logs = self.get_log('driver')
        logger.debug(f'get_log_driver :: {len(logs)} logs')
        logger.info(f'get_log_driver :: done')
        return logs

    def get_log_performance(self) -> list:
        """Get performance logs"""
        logger.debug(f'get_log_performance')
        logs = self.get_log('performance')
        logger.debug(f'get_log_performance :: {len(logs)} logs')
        logger.info(f'get_log_performance :: done')
        return logs

    def check_page_load_finished(self) -> bool:
        """Checks for `frameStoppedLoading` string in performance logs"""
        logger.debug(f'check_page_load_finished :: checking')

        logs = self.get_log_performance()
        logger.debug(f'check_page_load_finished :: checking :: {len(logs)} logs found')

        check = []
        for log_dict in logs:
            # logger.debug(f'check_page_load_finished :: checking :: {log_dict}')
            if 'frameStoppedLoading' in log_dict.get('message'):
                logger.debug(f'check_page_load_finished :: checking :: frameStoppedLoading :: found :: {log_dict}')
                check.append(log_dict)

        if check:
            logger.info(f'check_page_load_finished :: checking :: done')
            return True

        logger.error(f'check_page_load_finished :: checking :: not finished loading')
        return False

    @property
    def keys(self):
        """Set of special keys codes"""
        return selenium.webdriver.common.keys.Keys

    def refresh(self) -> None:
        """refresh the page"""
        logger.debug(f'refresh :: {self.current_url=}')
        refresh = self.webdriver.refresh()
        logger.info(f'refresh :: done')
        return refresh

    @property
    def url(self):
        """alias to current_url"""
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
        return ''

    @property
    def window_size(self):
        return self.config.webdriver_wrapper.window_size

    def _screenshot_name(self, prefix=None):
        """Generate a unique filename"""
        logger.debug(f'_screenshot_name :: {prefix=}')

        title = self.webdriver.title
        url = self.current_url

        hostname = urlparse(url).hostname

        timestamp = Dates.filename_timestamp()
        hostname_ = Sanitation.ascii_numeric_only(hostname)
        title_ = Sanitation.ascii_numeric_only(title)

        logger.debug(f'_screenshot_name :: {url=}')
        logger.debug(f'_screenshot_name :: {timestamp=}')
        logger.debug(f'_screenshot_name :: {title_=}')
        logger.debug(f'_screenshot_name :: {hostname_=}')

        if prefix:
            prefix = Sanitation.safe_string(prefix)
            _screenshot_name = f'{prefix}_{timestamp}_{hostname_}_{title_}.png'
            logger.info(f'_screenshot_name :: {_screenshot_name=}')
            return _screenshot_name

        _screenshot_name = f'{timestamp}_{hostname_}_{title_}.png'
        logger.debug(f'_screenshot_name :: {_screenshot_name=}')

        logger.debug(f'_screenshot_name :: done')
        return _screenshot_name

    def action_click(
            self,
            element: selenium.webdriver.remote.webelement.WebElement, **kwargs):
        """perform mouse click"""
        logger.debug(f'action_click :: {element=} :: {kwargs=}')
        try:
            logger.debug(f'action_click :: tag_name :: {element.tag_name}')
            logger.debug(f'action_click :: text :: {element.text}')
            logger.debug(f'action_click :: accessible_name :: {element.accessible_name}')
            logger.debug(f'action_click :: aria_role :: {element.aria_role}')

            element.click(**kwargs)
            logger.info(f'action_click :: done')
            return True

        except Exception as error:
            raise Exception(f'action_click :: failed :: {error=} :: {element=}')

    def action_type(
            self,
            key: str or Keys,
            secret: bool = False) -> selenium.webdriver.common.action_chains.ActionChains:
        """perform keyboard command"""

        if secret:
            logger.debug(f'action_type :: {f"*" * len(f"{key}")}')
        else:
            logger.debug(f'action_type :: {key}')

        try:
            action_type = selenium.webdriver.common.action_chains.ActionChains(
                self.webdriver).send_keys(key).perform()
            logger.info(f'action_type :: done')
            return action_type

        except Exception as error:
            raise Exception(f'action_type :: failed :: {error=} :: {key=}')

    def action_type_up(
            self,
            key: str or Keys,
            secret: bool = False) -> selenium.webdriver.common.action_chains.ActionChains:
        """release key"""

        if secret:
            logger.debug(f'action_type_up :: {"*" * len(f"{key}")}')
        else:
            logger.debug(f'action_type_up :: {key}')

        try:
            action_type_up = selenium.webdriver.common.action_chains.ActionChains(
                self.webdriver).key_up(key).perform()
            logger.info(f'action_type_up :: done')
            return action_type_up

        except Exception as error:
            raise Exception(f'action_type_up :: failed :: {error=} :: {key=}')

    def action_type_down(
            self,
            key: str or Keys,
            secret: bool = False, ) -> selenium.webdriver.common.action_chains.ActionChains:
        """hold key down"""

        if secret:
            logger.debug(f'action_type_down :: {"*" * len(f"{key}")}')
        else:
            logger.debug(f'action_type_down :: {key}')

        try:
            action_type_down = selenium.webdriver.common.action_chains.ActionChains(
                self.webdriver).key_down(key).perform()
            logger.info(f'action_type_down :: done')
            return action_type_down

        except Exception as error:
            raise Exception(f'action_type_down :: failed :: {error=} :: {key=}')

    def add_cookie(self, cookie_dict: dict) -> bool:
        logger.debug(
            f'add_cookie :: {cookie_dict.get("domain")} :: '
            f'{cookie_dict.get("path")} :: '
            f'{cookie_dict.get("secure")} :: '
            f'{cookie_dict.get("expiry")} :: '
            f'{cookie_dict.get("name")}'
        )

        result = self.webdriver.add_cookie(cookie_dict=cookie_dict)

        if result is None:
            logger.info(f'add_cookie :: done')
            return True

        raise Exception(f'add_cookie :: failed :: {cookie_dict=}')

    def add_cookie_from_file(self, file: str) -> bool:
        """add cookies from file"""
        logger.debug(f'add_cookie_from_file :: {file=}')

        if os.path.exists(file):
            self.add_cookies_from_list(
                self.cookie_file_to_dict(file=file)
            )
            logger.info(f'add_cookie_from_file :: done')
            return True

        raise Exception(f'add_cookie_from_file :: failed :: {file=}')

    def add_cookies_from_list(self, cookies_list: list) -> bool:
        """add cookies from a list of cookies"""
        logger.debug(f'add_cookies_from_list :: {len(cookies_list)} cookies found')

        for cookie in cookies_list:
            self.add_cookie(cookie_dict=cookie)

        logger.debug(f'add_cookies_from_list :: {len(cookies_list)} cookies added')
        logger.info(f'add_cookies_from_list :: done')
        return True

    def add_cookie_from_current_url(self):
        """add cookies from the current url"""
        logger.debug(f'add_cookie_from_current_url :: {self.url=}')
        logger.info(f'add_cookie_from_current_url :: done')
        return self.add_cookie_from_url(self.url)

    def add_cookie_from_url(self, url: str) -> bool:
        """add cookies from matching hostname"""
        logger.debug(f'add_cookie_from_url :: {url=}')

        cookie_file = self._url_filename(url=url)
        logger.debug(f'add_cookie_from_url :: {cookie_file=}')

        if os.path.exists(cookie_file):
            logger.debug(f'add_cookie_from_url :: {cookie_file=} file found')
            add_cookie_from_url = self.add_cookie_from_file(file=cookie_file)
            logger.info(f'add_cookie_from_url :: done')
            return add_cookie_from_url

        logger.error(f'add_cookie_from_url :: failed :: file not found :: {cookie_file=}')
        raise Exception(f'add_cookie_from_url :: failed :: file not found :: {cookie_file=}')

    def add_cookie_from_base64(self, base64_str: str) -> bool:
        """add cookie from base64 string"""
        logger.debug(f'add_cookie_from_base64 :: base64 :: {len(base64_str) / 1024} KB')

        if base64_str:
            add_cookie_from_base64 = json.loads(base64.b64decode(base64_str))
            logger.debug(f'add_cookie_from_base64 :: str :: {len(add_cookie_from_base64) / 1024} KB')
            self.add_cookies_from_list(add_cookie_from_base64)

            logger.info(f'add_cookie_from_base64 :: done')
            return True

        raise Exception(f'add_cookie_from_base64 :: failed :: {len(base64_str) / 1024} KB')

    def autosave_cookies(self) -> bool:
        """auto save cookies for current url"""
        logger.debug(f'autosave_cookies :: {self.current_url=}')

        if self.current_url:

            if not self.autosaved:
                logger.debug(f'autosave_cookies :: {self.autosaved=}')
                try:
                    self.add_cookie_from_current_url()
                except:
                    logger.debug(f'autosave_cookies :: no cookies for {self.current_url=}')
                self.refresh()
                self.autosaved = True
                logger.debug(f'autosave_cookies :: {self.autosaved=}')

            autosave_cookies = self.save_cookies_for_current_url()
            logger.info(f'autosave_cookies :: done')
            return autosave_cookies

        logger.debug(f'autosave_cookies :: failed :: no current url :: {self.current_url=}')

    def delete_all_cookies(self) -> None:
        """delete all cookies"""
        logger.debug(f'delete_all_cookies')
        delete_all_cookies = self.webdriver.delete_all_cookies()
        logger.info(f'delete_all_cookies :: done')
        return delete_all_cookies

    def _url_filename(self, url: str):
        """turn url into a filename"""
        logger.debug(f'_url_filename :: {url=}')

        parsed = self.urlparse(url)
        hostname = parsed.hostname
        cookie_file = f'cookies-{hostname}.json'

        logger.debug(f'_url_filename :: {hostname=}')
        logger.debug(f'_url_filename :: {cookie_file=}')

        logger.debug(f'_url_filename :: done')
        return cookie_file

    def get_cookie(self, name: str) -> dict:
        """get cookie by name"""
        logger.debug(f'get_cookie :: {name=}')
        get_cookie = self.webdriver.get_cookie(name=name)
        logger.debug(f'get_cookie :: {get_cookie=}')
        logger.info(f'get_cookie :: done')
        return get_cookie

    def get_cookies(self) -> [dict]:
        """get all cookies"""
        logger.debug(f'get_cookies :: ')
        get_cookies = self.webdriver.get_cookies()
        logger.debug(f'get_cookies :: {len(get_cookies)} total cookies')
        logger.info(f'get_cookies :: done')
        return get_cookies

    def get_cookies_base64(self) -> str:
        """get cookies as base64"""
        logger.debug(f'get_cookies_base64 ::')

        get_cookies_base64 = self.get_cookies()
        get_cookies_base64 = base64.b64encode(
            json.dumps(get_cookies_base64).encode()
        ).decode()
        logger.debug(f'get_cookies_base64 :: {len(get_cookies_base64) / 1024} KB')

        logger.info(f'get_cookies_base64 :: done')
        return get_cookies_base64

    def get_cookies_json(self) -> json.dumps:
        """get cookies as json"""
        logger.debug(f'get_cookies_json ::')

        get_cookies_json = self.get_cookies()
        get_cookies_json = json.dumps(get_cookies_json)
        logger.debug(f'get_cookies_json :: {len(get_cookies_json) / 1024} KB')

        logger.info(f'get_cookies_json :: done')
        return get_cookies_json

    def get_cookies_summary(self) -> dict:
        """get cookies summary"""
        logger.debug(f'get_cookies_summary ::')

        result = self.get_cookies()
        summary = {}
        if result:
            for cookie in result:
                cookie = dict(cookie)
                domain = cookie.get('domain')
                name = cookie.get('name')
                expiry = cookie.get('expiry')

                logger.debug(f'get_cookies_summary :: {cookie}')
                logger.debug(f'get_cookies_summary :: domain :: {domain}')
                logger.debug(f'get_cookies_summary :: name :: {name}')
                logger.debug(f'get_cookies_summary :: expiry :: {expiry}')

                if domain in summary.keys():
                    summary[domain].append(cookie)
                else:
                    summary[domain] = [cookie]

        logger.debug(f'get_cookies_summary :: summary :: {summary}')
        logger.info(f'get_cookies_summary ::')
        return summary

    def close(self):
        """close browser"""
        logger.debug(f'webdriver :: close')
        self.webdriver.close()
        logger.info(f'webdriver :: close :: done')

    @staticmethod
    def error_parsing(error) -> tuple:
        """parse webdriver error"""
        logger.debug(f'error_parsing :: {error=}')

        try:
            error_parsed = f'{error}'.splitlines()
            error_parsed = [f'{x}'.strip() for x in error_parsed]
            message = error_parsed[0]
            session = error_parsed[1]
            stacktrace = error_parsed[2:]
            stacktrace = ' '.join(stacktrace)

            logger.debug(f'error_parsing :: {error_parsed}')
            logger.debug(f'error_parsing :: {message}')
            logger.debug(f'error_parsing :: {stacktrace}')

            logger.info(f'error_parsing :: done')
            return message, session, stacktrace

        except Exception as exception:
            logger.error(f'error_parsing :: failed :: {exception=}')
            return error, None, None

    def find_all_with_beautifulsoup(
            self,
            name=None,
            attrs={},
            recursive=True,
            string=None,
            limit=None,
            case_sensitive=False,
            **kwargs) -> list:
        """find all with BeautifulSoup"""

        BeautifulSoup = self.get_page_source_beautifulsoup()

        if string:
            string_compiled = re.compile(string)

            if case_sensitive is False:
                string_compiled = re.compile(string, re.IGNORECASE)

            string = string_compiled

        RESULTS = BeautifulSoup.find_all(
            name=name,
            attrs=attrs,
            recursive=recursive,
            string=string,
            limit=limit,
            **kwargs,
        )

        logger.debug(f'find_all_with_beautifulsoup :: {RESULTS}')
        logger.info(f'find_all_with_beautifulsoup :: {len(RESULTS)} results')

        return RESULTS

    def find_anything(
            self,
            match: str,
            value: str = None,
            value_attr: str = None,
            by: selenium.webdriver.common.by.By = None,
            case_sensitive: bool = False,
            exact_match: bool = False,
            return_first: bool = False,
            caching: bool = False,
            **kwargs) -> list:
        """fuzzy search through everything

        find all tags
        find all matches within meta data

        this is very slow. it takes upwards of 1 minutes per loop of all elements

        """
        logger.debug(
            f'find_anything :: '
            f'{match=} :: '
            f'{value=} :: '
            f'{value_attr=} :: '
            f'{by=} :: '
            f'{case_sensitive=} :: '
            f'{exact_match=} :: '
            f'{return_first=} :: '
            f'{caching=} :: '
            f' {kwargs=}'
        )

        by_types = [
            self.by.XPATH,
            self.by.TAG_NAME,
            self.by.ID,
            self.by.NAME,
            self.by.CLASS_NAME,
            self.by.LINK_TEXT,
            self.by.PARTIAL_LINK_TEXT,
            self.by.CSS_SELECTOR,
        ]

        if by:
            by_types = [by]

        if not value:
            value = '*'

        MATCHED = []

        for by_ in by_types:
            elements = self.find_elements(value=value, by=by_, caching=caching, **kwargs)

            for element in elements:

                if value_attr:
                    dirs = [value_attr]
                else:
                    dirs = dir(element)

                dir_meta = []
                for dir_ in dirs:

                    try:
                        dir_meta.append(
                            getattr(element, f'{dir_}')
                        )

                        MATCH = f'{match}'
                        AGAINST = f'''{getattr(element, f'{dir_}')}'''

                        if not case_sensitive:
                            MATCH = f'{match}'.lower()
                            AGAINST = f'''{getattr(element, f'{dir_}')}'''.lower()

                        FOUND = None

                        if MATCH == AGAINST and exact_match:
                            FOUND = element

                        if MATCH in AGAINST and not exact_match:
                            FOUND = element

                        if FOUND and FOUND not in MATCHED:
                            logger.debug(
                                f'find_anything :: '
                                f'{self.current_url} :: '
                                f'{MATCH=} :: '
                                f'{AGAINST=} :: '
                                f'attribute={dir_} :: '
                                f'{element=} :: '
                                f'found'
                            )
                            MATCHED.append(FOUND)

                            if return_first:
                                logger.info(f'find_anything :: done')
                                return MATCHED

                    except Exception as error:
                        logger.error(f'find_anything :: error :: {error=} :: {error.msg=}')

        logger.debug(f'find_anything :: {len(MATCHED)} results found')
        logger.info(f'find_anything :: done')
        return MATCHED

    def find_anything_with_beautifulsoup(
            self,
            match: str,
            name: str = None,
            attrs: dict = {},
            recursive: bool = True,
            string: str = None,
            limit: int = None,
            case_sensitive: bool = False,
            **kwargs) -> bs4.BeautifulSoup:
        """find anything with fuzzy search in beaurifulsoup

        """
        logger.debug(
            f'find_anything_with_beautifulsoup :: '
            f'{match=} :: '
            f'{name=} :: '
            f'{attrs=} :: '
            f'{recursive=} :: '
            f'{string=} :: '
            f'{limit=} :: '
            f'{case_sensitive=} :: '
            f' {kwargs=}'
        )

        MATCHES = []

        results = self.find_all_with_beautifulsoup(
            name=name,
            attrs=attrs,
            recursive=recursive,
            string=string,
            limit=limit,
            case_sensitive=case_sensitive)

        for element in results:

            findall = re.compile(match).findall(str(element))
            if findall:
                logger.debug(f'find_anything_with_beautifulsoup :: found :: {element}')
                MATCHES.append(element)

        logger.info(f'find_anything_with_beautifulsoup :: MATCHES :: {len(MATCHES)} found')
        return MATCHES

    def find_element(
            self,
            value: str,
            by: selenium.webdriver.common.by.By,
            **kwargs) -> selenium.webdriver.Chrome.find_element:
        """find element"""
        logger.debug(f'find_element :: {self.current_url} :: {value=} :: {by=} :: {kwargs=}')

        find_element = self.webdriver.find_element(value=value, by=by, **kwargs)
        logger.debug(f'find_element :: {self.current_url} :: {value=} :: found')

        logger.info(f'find_element :: done')
        return find_element

    def find_elements(
            self,
            value: str,
            by: selenium.webdriver.common.by.By,
            caching: bool = False,
            **kwargs) -> list:
        """find elements"""
        logger.debug(f'find_elements :: {self.current_url} :: {value=} :: {by=} :: {kwargs=}')

        # try caching the elements
        if caching:
            if by not in self.cache.keys():
                self.cache[by] = {}
                self.cache[by][value] = self.webdriver.find_elements(value=value, by=by, **kwargs)

            elif value not in self.cache[by].keys():
                self.cache[by][value] = self.webdriver.find_elements(value=value, by=by, **kwargs)

        else:
            self.cache[by] = {}
            self.cache[by][value] = self.webdriver.find_elements(value=value, by=by, **kwargs)

        find_elements = self.cache[by][value]
        logger.debug(f'find_elements :: {len(find_elements)} elements found')

        logger.info(f'find_elements :: done')
        return find_elements

    def find_xpath(
            self,
            value: str,
            by: selenium.webdriver.common.by.By = selenium.webdriver.common.by.By.XPATH,
            **kwargs) -> selenium.webdriver.Chrome.find_element:
        """find xpath"""
        logger.debug(f'find_xpath :: {self.current_url} :: {value=} :: {by=} :: {kwargs=}')

        find_xpath = self.find_element(value=value, by=by, **kwargs)
        logger.debug(f'find_xpath :: {self.current_url} :: {find_xpath=} :: found')

        logger.info(f'find_xpath :: done')
        return find_xpath

    def get(self, url: str, **kwargs) -> bool:
        """get url"""
        logger.debug(f'browser :: get :: {url} :: {kwargs=}')

        if not self.webdriver:
            raise Exception(f'browser :: get :: failed :: missing webdriver')

        try:
            if self.webdriver.get(url, **kwargs) is None:
                logger.debug(f'browser :: get :: {url} :: {self.current_url=} :: {kwargs=}')
                logger.info(f'browser :: get')

            if self.config.cookies_autosave:
                self.autosave_cookies()

            logger.info(f'browser :: get :: done')
            return True

        except Exception as exception:
            logger.error(f'browser :: get :: failed :: {exception=}')

        logger.error(f'browser :: get :: failed :: {url}')
        return False

    def get_page(self, *args, **kwargs) -> bool:
        """alias to get"""
        logger.debug(f'get_page :: {args=} :: {kwargs=}')
        return self.get(*args, **kwargs)

    def get_page_source(self) -> str:
        """get page source"""
        logger.debug(f'get_page_source :: ')
        get_page_source = self.webdriver.page_source
        logger.debug(f'get_page_source :: {len(get_page_source) / 1024} KB')
        logger.info(f'get_page_source :: done')
        return get_page_source

    def get_page_source_beautifulsoup(
            self,
            markup: str = None,
            features: str = 'lxml') -> bs4.BeautifulSoup:
        """read page source with beautifulsoup"""

        if not markup:
            markup = self.get_page_source()

        logger.debug(f'get_page_source_beautifulsoup :: {features=} :: {len(markup) / 1024} KB')

        get_page_source_beautifulsoup = bs4.BeautifulSoup(
            markup=markup,
            features=features)
        logger.debug(f'get_page_source_beautifulsoup :: {len(get_page_source_beautifulsoup)} size')

        logger.info(f'get_page_source_beautifulsoup :: done')
        return get_page_source_beautifulsoup

    def get_random_user_agent(
            self,
            filter: list or str = None,
            case_sensitive: bool = False) -> str:
        """get a random user agent string"""
        logger.debug(f'get_random_user_agent :: {filter=} :: {case_sensitive=}')

        get_random_user_agent = SeleniumUserAgentBuilder().get_random_agent(
            filter=filter,
            case_sensitive=case_sensitive)
        logger.debug(f'get_random_user_agent :: {get_random_user_agent}')

        logger.info(f'get_random_user_agent :: done')
        return get_random_user_agent

    def get_screenshot_as_base64(self, **kwargs):
        """screenshot as base64"""
        logger.debug(f'get_screenshot_as_base64 :: ')
        get_screenshot_as_base64 = self.webdriver.get_screenshot_as_base64(**kwargs)
        logger.debug(f'get_screenshot_as_base64 :: {round(len(get_screenshot_as_base64) / 1024)} KB')
        logger.info(f'get_screenshot_as_base64 :: done')
        return get_screenshot_as_base64

    def get_screenshot_as_file(
            self,
            filename: str = None,
            prefix: str = None,
            folder: str = None,
            **kwargs) -> bool:
        """alias to save_screenshot"""
        logger.debug(f'get_screenshot_as_file :: {filename=} :: {prefix=} :: {folder=} :: {kwargs=}')

        get_screenshot_as_file = self.save_screenshot(
            self,
            filename=filename,
            prefix=prefix,
            folder=folder,
            **kwargs)

        logger.info(f'get_screenshot_as_file :: done')
        return get_screenshot_as_file

    def get_screenshot_as_png(self, **kwargs):
        """screenshot as png"""
        logger.debug(f'get_screenshot_as_png ::')
        get_screenshot_as_png = self.webdriver.get_screenshot_as_png(**kwargs)
        logger.debug(f'get_screenshot_as_png :: {round(len(get_screenshot_as_png) / 1024)} KB')
        logger.info(f'get_screenshot_as_png :: done')
        return get_screenshot_as_png

    def is_running(self) -> bool:
        """webdriver is running"""
        logger.debug(f'webdriver :: ')

        if self.webdriver:
            logger.info(f'webdriver :: is running')
            return True
        logger.error(f'webdriver :: is not running')
        return False

    def load_cookies_for_current_url(self) -> bool:
        """load cookies from file for current url"""
        logger.debug(f'load_cookies_for_current_url :: ')

        filename = self._url_filename(url=self.url)
        logger.debug(f'load_cookies_for_current_url :: {filename=} :: {self.url=}')

        load_cookies_for_current_url = self.add_cookie_from_file(file=filename)
        logger.info(f'load_cookies_for_current_url :: done')
        return load_cookies_for_current_url

    @property
    def page_source(self):
        return self.webdriver.page_source

    def urlparse(self, url: str):
        """parse url"""
        logger.debug(f'urlparse :: {url=}')
        parsed = urlparse(url=url)
        logger.debug(f'urlparse :: {parsed=}')
        logger.info(f'urlparse :: done')
        return parsed

    def quit(self) -> bool:
        """gracefully quit webdriver"""
        logger.debug(f'webdriver :: quit')

        if self.webdriver:
            try:
                self.close()
                self.webdriver.quit()
                self.webdriver.stop_client()
            except Exception as error:
                message, session, stacktrace = self.error_parsing(error)
                logger.error(f'webdriver :: quit :: failed :: {message=} :: {session=} :: {stacktrace=}')
                return False

        logger.info(f'webdriver :: quit :: done')
        return True

    def run(self) -> bool:
        """run webdriver"""
        logger.debug(f'webdriver :: run')

        try:
            run = self.config.run()
            logger.info(f'webdriver :: run :: done')
            return run
        except Exception as exception:
            logger.error(f'webdriver :: run :: failed :: {exception=}')
            raise Exception(f'webdriver :: run :: failed :: {exception=}')

    def save_cookies_for_current_url(self) -> bool:
        """save cookies for current url"""
        logger.debug(f'save_cookies_for_current_url :: ')

        filename = self._url_filename(url=self.url)
        save_cookies_for_current_url = self.save_cookies_to_file(file=filename)
        logger.debug(f'save_cookies_for_current_url :: {self.current_url} :: {filename}')

        logger.info(f'save_cookies_for_current_url :: done')
        return save_cookies_for_current_url

    def save_cookies_to_file(self, file: str) -> bool:
        """save cookies to file"""
        logger.debug(f'save_cookies_to_file :: {file}')

        with open(file, 'w') as cookies:
            cookies.write(
                self.get_cookies_json()
            )

        if os.path.exists(file):
            logger.debug(f'save_cookies_to_file :: {os.path.abspath(file)} :: {os.stat(file).st_size} B')
            logger.info(f'save_cookies_to_file :: done')
            return True

        logger.error(f'save_cookies_to_file :: failed :: {file=}')
        return False

    def save_screenshot(
            self,
            filename: str = None,
            prefix: str = None,
            folder: str = None,
            **kwargs) -> bool:
        """save screenshot to file"""
        logger.debug(f'save_screenshot :: {self.current_url} :: {filename=} :: {prefix=} :: {folder=} :: {kwargs=}')

        if not filename:
            filename = self._screenshot_name(prefix)
            logger.debug(f'save_screenshot :: {filename=}')

        if not folder:
            path = os.path.abspath(tempfile.gettempdir())
            logger.debug(f'save_screenshot :: {path=}')
        else:
            path = os.path.abspath(folder)
            logger.debug(f'save_screenshot :: {path=}')

        if not os.path.exists(path):
            os.makedirs(path)

        save = os.path.join(path, filename)

        if self.webdriver.save_screenshot(save, **kwargs):
            logger.debug(f'save_screenshot :: {save} :: {round(os.stat(save).st_size / 1024)} KB')
            logger.info(f'save_screenshot :: done')
            return True

        logger.error(f'save_screenshot :: failed')
        return False

    def set_window_size(self, width=1920, height=1080, device_type=None) -> bool:
        """set browser resolution"""
        logger.debug(f'set_window_size :: {width=} :: {height=} :: {device_type=}')

        try:
            self.config.webdriver_wrapper.set_window_size(
                width=width,
                height=height,
                device_type=device_type)
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            logger.error(f'set_window_size :: failed :: {message=} :: {session=} :: {stacktrace=}')
            return False

        logger.info(f'set_window_size :: done')
        return True

    def set_window_position(self, x: int = 0, y: int = 0):
        """set browser position"""
        logger.debug(f'set_window_position :: {x=} :: {y=}')
        set_window_position = self.webdriver.set_window_position(x, y)
        logger.info(f'set_window_position :: done')
        return set_window_position

    def start(self):
        """alias to run"""
        return self.run()

    def switch_to_new_window_tab(self):
        """Opens a new tab and switches to new tab"""
        self.webdriver.switch_to.new_window('tab')
        logger.debug(f'switch_to_new_window_tab :: {self.webdriver.current_window_handle=}')
        logger.info(f'switch_to_new_window_tab :: done')

    def switch_to_new_window_window(self):
        """Opens a new window and switches to new window"""
        self.webdriver.switch_to.new_window('window')
        logger.debug(f'switch_to_new_window_window :: {self.webdriver.current_window_handle=}')
        logger.info(f'switch_to_new_window_window :: done')

    def wait_for_anything(
            self,
            match: str,
            value: str = None,
            value_attr: str = None,
            by: selenium.webdriver.common.by.By = None,
            case_sensitive: bool = False,
            exact_match: bool = False,
            return_first: bool = False,
            timeout: int = 30,
            **kwargs) -> list:
        """wait for anything"""
        logger.debug(
            f'wait_for_anything :: '
            f'{match=} :: '
            f'{value=} :: '
            f'{value_attr=} :: '
            f'{by=} :: '
            f'{case_sensitive=} :: '
            f'{exact_match=} :: '
            f'{timeout=} :: '
            f'{return_first=} :: '
            f'{kwargs=}'
        )

        timeout_start = time.time()
        timeout_elapsed = round(abs(timeout_start - time.time()), 1)

        while timeout_elapsed < timeout:

            logger.debug(
                f'wait_for_anything :: '
                f'timeout {timeout_elapsed}/{timeout} sec :: '
                f'{self.current_url=} :: '
                f'{value=} :: '
                f'{by=}'
            )

            try:
                find = self.find_anything(
                    match=match,
                    value=value,
                    value_attr=value_attr,
                    by=by,
                    case_sensitive=case_sensitive,
                    exact_match=exact_match,
                    return_first=return_first,
                    **kwargs)
                logger.debug(f'wait_for_anything :: {len(find)} elements found')

                if find:
                    logger.info(f'wait_for_anything :: done')
                    return find

            except Exception as error:
                logger.error(
                    f'wait_for_anything :: '
                    f'failed :: '
                    f'timeout {timeout_elapsed}/{timeout} sec :: '
                    f'{error=} :: '
                    f'{match=} :: '
                    f'{value=} :: '
                    f'{by=}'
                )

            timeout_elapsed = round(abs(timeout_start - time.time()), 1)

        logger.error(f'wait_for_anything :: failed :: {match=} :: {value=} :: {by=}')
        return []

    def wait_for_element(
            self,
            value: str,
            by: selenium.webdriver.common.by.By,
            timeout: int = 30,
            **kwargs) -> selenium.webdriver.Chrome.find_element:
        """wait for an element"""
        logger.debug(f'wait_for_element :: {value=} :: {by=} :: {timeout=} :: {kwargs=}')

        timeout_start = time.time()
        timeout_elapsed = round(abs(timeout_start - time.time()), 1)

        while timeout_elapsed < timeout:

            logger.debug(
                f'wait_for_element :: '
                f'timeout {timeout_elapsed}/{timeout} sec :: '
                f'{by=} :: '
                f'{self.current_url} :: '
                f'{value=}'
            )

            try:
                find = self.find_element(
                    value=value,
                    by=by,
                    **kwargs)
                logger.debug(f'wait_for_element :: element found')

                if find:
                    logger.info(f'wait_for_element :: done')
                    return find

            except Exception as error:
                logger.error(
                    f'wait_for_element :: '
                    f'failed :: '
                    f'timeout {timeout_elapsed}/{timeout} sec :: '
                    f'{error=} :: '
                    f'{value=} :: '
                    f'{by=}'
                )

            timeout_elapsed = round(abs(timeout_start - time.time()), 1)

        logger.error(f'wait_for_element :: failed :: {value=} :: {by=}')
        return

    def wait_for_elements(
            self,
            value: str,
            by: selenium.webdriver.common.by.By,
            timeout: int = 30,
            **kwargs) -> list:
        """wait for all matching elements"""
        logger.debug(f'wait_for_elements :: {value=} :: {by=} :: {timeout=} :: {kwargs=}')

        timeout_start = time.time()
        timeout_elapsed = round(abs(timeout_start - time.time()), 1)

        while timeout_elapsed < timeout:

            logger.debug(
                f'wait_for_element :: '
                f'timeout {timeout_elapsed}/{timeout} sec :: '
                f'{by=} :: '
                f'{self.current_url} :: '
                f'{value=}'
            )

            try:
                find = self.find_elements(
                    value=value,
                    by=by,
                    **kwargs)
                logger.debug(f'wait_for_elements :: {len(find)} elements found')

                if find:
                    logger.info(f'wait_for_elements :: done')
                    return find

            except Exception as error:
                logger.error(f'wait_for_elements :: failed :: {error=} :: {value=} :: {by=}')

            timeout_elapsed = round(abs(timeout_start - time.time()), 1)

        logger.error(f'wait_for_elements :: failed :: {value=} :: {by=}')
        return []

    def wait_for_id(
            self,
            value: str,
            timeout: int = 30,
            **kwargs) -> selenium.webdriver.Chrome.find_element:
        """wait for an element id"""
        logger.debug(f'wait_for_id :: {value=} :: {timeout=} :: {kwargs=}')
        wait_for_id = self.wait_for_element(
            value=value,
            by=self.by.ID,
            timeout=timeout,
            **kwargs)

        logger.info(f'wait_for_id :: done')
        return wait_for_id

    def wait_for_xpath(
            self,
            value: str,
            timeout: int = 30,
            **kwargs) -> selenium.webdriver.Chrome.find_element:
        """wait for a xpath"""
        logger.debug(f'wait_for_xpath :: {value=} :: {timeout=} :: {kwargs=}')

        wait_for_xpath = self.wait_for_element(
            value=value,
            by=self.by.XPATH,
            timeout=timeout,
            **kwargs)

        logger.info(f'wait_for_xpath :: done')
        return wait_for_xpath
