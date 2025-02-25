import os
import re
import bs4
import json
import time
import urllib
import urllib.parse
import base64
import pandas
import datetime
import tempfile
import traceback

import selenium
import selenium.webdriver
import selenium.webdriver.common.by
import selenium.webdriver.remote.webelement

from selenium.webdriver.common.keys import Keys

import automon

from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO
from automon.helpers.dates import Dates
from automon.helpers.sleeper import Sleeper
from automon.helpers.sanitation import Sanitation
from automon.integrations.beautifulsoupWrapper import BeautifulSoupClient

from .config import SeleniumConfig
from .user_agents import SeleniumUserAgentBuilder
from .exceptions import *

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


class SeleniumBrowser(object):
    config: SeleniumConfig
    webdriver: selenium.webdriver
    status: int

    def __init__(self, config: SeleniumConfig = None):
        """A selenium wrapper"""

        self._config = config or SeleniumConfig()
        self._selenium = selenium

        self.autosave_cookies = None

        self._logs = {}
        self.cache = {}

    def __repr__(self):
        try:
            return (
                f'[SeleniumBrowser] :: '
                f'{self.config.webdriver_wrapper} :: '
                f'{self.webdriver=} :: '
                f'{self.user_agent=}'
            )
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
        logger.debug(f'[SeleniumBrowser] :: cookie_file_to_dict :: {file=}')
        with open(file, 'r') as file:
            logger.debug(f'[SeleniumBrowser] :: cookie_file_to_dict :: read :: {file=}')
            logger.info(f'[SeleniumBrowser] :: [SeleniumBrowser] :: cookie_file_to_dict :: read :: done')
            return json.loads(file.read())

    @property
    def _current_url(self):
        """get browser current url"""
        try:
            return self.webdriver.current_url
        except Exception as error:
            return

    @property
    def current_url(self):
        if self.webdriver:
            if self._current_url == 'data:,':
                return ''
            return self._current_url
        return ''

    @property
    def current_window_handle(self):
        if self.webdriver:
            return self.webdriver.current_window_handle

    @property
    def webdriver(self):
        """get webdriver"""
        return self.config.webdriver

    def check_page_load_finished(self) -> bool:
        """Checks for `frameStoppedLoading` string in performance logs"""
        logger.debug(f'[SeleniumBrowser] :: check_page_load_finished :: checking')

        logs = self.get_log_performance()
        logger.debug(f'[SeleniumBrowser] :: check_page_load_finished :: checking :: {len(logs)} logs found')

        check = []
        for log_dict in logs:
            # logger.debug(f'[SeleniumBrowser] :: check_page_load_finished :: checking :: {log_dict}')
            if 'frameStoppedLoading' in log_dict.get('message'):
                logger.debug(
                    f'[SeleniumBrowser] :: check_page_load_finished :: checking :: frameStoppedLoading :: found :: {log_dict}')
                check.append(log_dict)

        if check:
            logger.info(f'[SeleniumBrowser] :: check_page_load_finished :: checking :: done')
            return True

        logger.error(f'[SeleniumBrowser] :: check_page_load_finished :: checking :: not finished loading')
        return False

    def action_click(
            self,
            element: selenium.webdriver.remote.webelement.WebElement, **kwargs):
        """perform mouse click"""
        logger.debug(f'[SeleniumBrowser] :: action_click :: {element=} :: {kwargs=}')
        try:
            logger.debug(f'[SeleniumBrowser] :: action_click :: tag_name :: {element.tag_name}')
            logger.debug(f'[SeleniumBrowser] :: action_click :: text :: {element.text}')
            logger.debug(f'[SeleniumBrowser] :: action_click :: accessible_name :: {element.accessible_name}')
            logger.debug(f'[SeleniumBrowser] :: action_click :: aria_role :: {element.aria_role}')

            element.click(**kwargs)
            logger.info(f'[SeleniumBrowser] :: action_click :: done')
            return True

        except Exception as error:
            raise Exception(f'[SeleniumBrowser] ::action_click :: failed :: {error=} :: {element=}')

    def action_scroll_to_bottom(self):
        return self.webdriver.execute_script("window.scrollTo(0, document.body.scrollHeight);") or True

    def action_scroll_down(self):
        return self.webdriver.execute_script("window.scrollBy(0,350)", "") or True

    def action_scroll_up(self):
        return self.webdriver.execute_script("window.scrollBy(0,-350)", "") or True

    def action_type(
            self,
            key: str or Keys,
            secret: bool = False) -> selenium.webdriver.common.action_chains.ActionChains:
        """perform keyboard command"""

        if secret:
            logger.debug(f'[SeleniumBrowser] :: action_type :: {f"*" * len(f"{key}")}')
        else:
            logger.debug(f'[SeleniumBrowser] :: action_type :: {key}')

        try:
            action_type = selenium.webdriver.common.action_chains.ActionChains(
                self.webdriver).send_keys(key).perform()
            logger.info(f'[SeleniumBrowser] :: action_type :: done')
            return action_type

        except Exception as error:
            raise Exception(f'[SeleniumBrowser] ::action_type :: failed :: {error=} :: {key=}')

    def action_type_up(
            self,
            key: str or Keys,
            secret: bool = False) -> selenium.webdriver.common.action_chains.ActionChains:
        """release key"""

        if secret:
            logger.debug(f'[SeleniumBrowser] :: action_type_up :: {"*" * len(f"{key}")}')
        else:
            logger.debug(f'[SeleniumBrowser] :: action_type_up :: {key}')

        try:
            action_type_up = selenium.webdriver.common.action_chains.ActionChains(
                self.webdriver).key_up(key).perform()
            logger.info(f'[SeleniumBrowser] :: action_type_up :: done')
            return action_type_up

        except Exception as error:
            raise Exception(f'[SeleniumBrowser] ::action_type_up :: failed :: {error=} :: {key=}')

    def action_type_down(
            self,
            key: str or Keys,
            secret: bool = False, ) -> selenium.webdriver.common.action_chains.ActionChains:
        """hold key down"""

        if secret:
            logger.debug(f'[SeleniumBrowser] :: action_type_down :: {"*" * len(f"{key}")}')
        else:
            logger.debug(f'[SeleniumBrowser] :: action_type_down :: {key}')

        try:
            action_type_down = selenium.webdriver.common.action_chains.ActionChains(
                self.webdriver).key_down(key).perform()
            logger.info(f'[SeleniumBrowser] :: action_type_down :: done')
            return action_type_down

        except Exception as error:
            raise Exception(f'[SeleniumBrowser] ::action_type_down :: failed :: {error=} :: {key=}')

    def add_cookie(self, cookie_dict: dict) -> bool:
        logger.debug(
            f'[SeleniumBrowser] :: add_cookie :: {cookie_dict.get("domain")} :: '
            f'path={cookie_dict.get("path")} :: '
            f'secure={cookie_dict.get("secure")} :: '
            f'expiry={cookie_dict.get("expiry")} :: '
            f'name={cookie_dict.get("name")}'
        )

        result = self.webdriver.add_cookie(cookie_dict=cookie_dict)

        if result is None:
            logger.info(f'[SeleniumBrowser] :: add_cookie :: done')
            return True

        raise Exception(f'[SeleniumBrowser] ::add_cookie :: failed :: {cookie_dict=}')

    def add_cookie_from_file(self, file: str) -> bool:
        """add cookies from file"""
        logger.debug(f'[SeleniumBrowser] :: add_cookie_from_file :: {file=}')

        if os.path.exists(file):
            self.add_cookies_from_list(
                self.cookie_file_to_dict(file=file)
            )
            logger.info(f'[SeleniumBrowser] :: add_cookie_from_file :: done')
            return True

        raise Exception(f'[SeleniumBrowser] ::add_cookie_from_file :: failed :: {file=}')

    def add_cookies_from_list(self, cookies_list: list) -> bool:
        """add cookies from a list of cookies"""
        logger.debug(f'[SeleniumBrowser] :: add_cookies_from_list :: {len(cookies_list)} cookies found')

        for cookie in cookies_list:
            self.add_cookie(cookie_dict=cookie)

        logger.debug(f'[SeleniumBrowser] :: add_cookies_from_list :: {len(cookies_list)} cookies added')
        logger.info(f'[SeleniumBrowser] :: add_cookies_from_list :: done')
        return True

    def add_cookie_from_current_url(self):
        """add cookies from the current url"""
        logger.debug(f'[SeleniumBrowser] :: add_cookie_from_current_url :: {self.url=}')
        logger.info(f'[SeleniumBrowser] :: add_cookie_from_current_url :: done')
        return self.add_cookie_from_url(self.url)

    def add_cookie_from_url(self, url: str) -> bool:
        """add cookies from matching hostname"""
        logger.debug(f'[SeleniumBrowser] :: add_cookie_from_url :: {url=}')

        cookie_file = self._url_filename(url=url)
        logger.debug(f'[SeleniumBrowser] :: add_cookie_from_url :: {cookie_file=}')

        if os.path.exists(cookie_file):
            logger.debug(f'[SeleniumBrowser] :: add_cookie_from_url :: {cookie_file=} file found')
            add_cookie_from_url = self.add_cookie_from_file(file=cookie_file)
            logger.info(f'[SeleniumBrowser] :: add_cookie_from_url :: done')
            return add_cookie_from_url

        logger.error(f'[SeleniumBrowser] :: add_cookie_from_url :: failed :: file not found :: {cookie_file=}')
        raise Exception(f'[SeleniumBrowser] ::add_cookie_from_url :: failed :: file not found :: {cookie_file=}')

    def add_cookie_from_base64(self, base64_str: str) -> bool:
        """add cookie from base64 string"""
        logger.debug(f'[SeleniumBrowser] :: add_cookie_from_base64 :: base64 :: {len(base64_str) / 1024} KB')

        if base64_str:
            add_cookie_from_base64 = json.loads(base64.b64decode(base64_str))
            logger.debug(
                f'[SeleniumBrowser] :: '
                f'add_cookie_from_base64 :: '
                f'str :: '
                f'{len(add_cookie_from_base64) / 1024} KB'
            )
            self.add_cookies_from_list(add_cookie_from_base64)

            logger.info(f'[SeleniumBrowser] :: add_cookie_from_base64 :: done')
            return True

        raise Exception(f'[SeleniumBrowser] ::add_cookie_from_base64 :: failed :: {len(base64_str) / 1024} KB')

    def autosaving_cookies(self) -> bool:
        """auto save cookies for current url"""
        logger.debug(f'[SeleniumBrowser] :: autosaving_cookies :: {self.current_url=}')

        autosave_cookies = self.autosave_cookies

        if self.current_url:

            if not autosave_cookies:
                logger.debug(f'[SeleniumBrowser] :: autosaving_cookies :: {autosave_cookies=}')
                try:
                    self.add_cookie_from_current_url()
                except:
                    logger.debug(f'[SeleniumBrowser] :: autosaving_cookies :: no cookies for {self.current_url=}')
                self.refresh()
                autosave_cookies = True
                self.autosave_cookies = autosave_cookies
                logger.debug(f'[SeleniumBrowser] :: autosaving_cookies :: {autosave_cookies=}')

            autosave_cookies = self.save_cookies_for_current_url()
            logger.info(f'[SeleniumBrowser] :: autosaving_cookies :: done')
            return autosave_cookies

        logger.debug(f'[SeleniumBrowser] :: autosaving_cookies :: failed :: no current url :: {self.current_url=}')

    def close(self):
        """close browser"""
        logger.debug(f'[SeleniumBrowser] :: close')
        self.webdriver.close()
        logger.info(f'[SeleniumBrowser] :: close :: done')

    def delete_all_cookies(self) -> None:
        """delete all cookies"""
        logger.debug(f'[SeleniumBrowser] :: delete_all_cookies')
        delete_all_cookies = self.webdriver.delete_all_cookies()
        logger.info(f'[SeleniumBrowser] :: delete_all_cookies :: done')
        return delete_all_cookies or True

    @staticmethod
    def error_parsing(error) -> tuple:
        """parse webdriver error"""
        logger.debug(f'[SeleniumBrowser] :: error_parsing :: {error=}')

        try:
            error_parsed = f'{error}'.splitlines()
            error_parsed = [f'{x}'.strip() for x in error_parsed]
            message = error_parsed[0]
            session = error_parsed[1]
            stacktrace = error_parsed[2:]
            stacktrace = ' '.join(stacktrace)

            logger.debug(f'[SeleniumBrowser] :: error_parsing :: {error_parsed}')
            logger.debug(f'[SeleniumBrowser] :: error_parsing :: {message}')
            logger.debug(f'[SeleniumBrowser] :: error_parsing :: {stacktrace}')

            logger.info(f'[SeleniumBrowser] :: error_parsing :: done')
            return message, session, stacktrace

        except Exception as exception:
            logger.error(f'[SeleniumBrowser] :: error_parsing :: failed :: {exception=}')
            return error, None, None

    def find_page_source_with_regex(self, regex: str, case_sensitive: bool = False):
        """find all with regex"""

        logger.debug(
            f'[SeleniumBrowser] :: find_all_with_re :: '
            f'{regex=} :: '
            f'{case_sensitive=}'
        )

        results = re.compile(regex)

        if case_sensitive:
            results = re.compile(regex, re.IGNORECASE)

        results = results.findall(self.page_source)

        logger.debug(f'[SeleniumBrowser] :: find_all_with_re :: {len(results)} results')
        logger.info(f'[SeleniumBrowser] :: find_all_with_re :: done')
        return results

    def find_all_with_beautifulsoup(
            self,
            name: str = None,
            attrs: dict = {},
            recursive: bool = True,
            string: str = None,
            limit: int = None,
            case_sensitive: bool = False,
            **kwargs) -> list:
        """find all with BeautifulSoup"""

        logger.debug(
            f'[SeleniumBrowser] :: find_all_with_beautifulsoup :: '
            f'{name=} :: '
            f'{attrs=} :: '
            f'{recursive=} :: '
            f'{string=} :: '
            f'{limit=} :: '
            f'{case_sensitive=} :: '
            f'{kwargs=}'
        )

        BeautifulSoup = self.get_page_source_beautifulsoup()

        if string:
            _string_compiled = re.compile(string)

            if case_sensitive is False:
                _string_compiled = re.compile(string, re.IGNORECASE)

            string = _string_compiled

        elements = BeautifulSoup.find_all(
            name=name,
            attrs=attrs,
            recursive=recursive,
            string=string,
            limit=limit,
            **kwargs,
        )

        logger.debug(f'[SeleniumBrowser] :: find_all_with_beautifulsoup :: {len(elements)} results')
        logger.info(f'[SeleniumBrowser] :: find_all_with_beautifulsoup :: done')

        return elements

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
            f'[SeleniumBrowser] :: find_anything :: '
            f'{match=} :: '
            f'{value=} :: '
            f'{value_attr=} :: '
            f'{by=} :: '
            f'{case_sensitive=} :: '
            f'{exact_match=} :: '
            f'{return_first=} :: '
            f'{caching=} :: '
            f'{kwargs=}'
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
                                f'[SeleniumBrowser] :: find_anything :: '
                                f'{self.current_url} :: '
                                f'{MATCH=} :: '
                                f'{AGAINST=} :: '
                                f'attribute={dir_} :: '
                                f'{element=} :: '
                                f'found'
                            )
                            MATCHED.append(FOUND)

                            if return_first:
                                logger.info(f'[SeleniumBrowser] :: find_anything :: done')
                                return MATCHED

                    except Exception as error:
                        logger.error(f'[SeleniumBrowser] :: find_anything :: error :: {error=} :: {error.msg=}')

        logger.debug(f'[SeleniumBrowser] :: find_anything :: {len(MATCHED)} results found')
        logger.info(f'[SeleniumBrowser] :: find_anything :: done')
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
            **kwargs) -> list:
        """find anything with fuzzy search in beaurifulsoup

        """
        logger.debug(
            f'[SeleniumBrowser] :: find_anything_with_beautifulsoup :: '
            f'{match=} :: '
            f'{name=} :: '
            f'{attrs=} :: '
            f'{recursive=} :: '
            f'{string=} :: '
            f'{limit=} :: '
            f'{case_sensitive=} :: '
            f'{kwargs=}'
        )

        MATCHES = []

        elements = self.find_all_with_beautifulsoup(
            name=name,
            attrs=attrs,
            recursive=recursive,
            string=string,
            limit=limit,
            case_sensitive=case_sensitive)

        logger.debug(
            f'[SeleniumBrowser] :: find_anything_with_beautifulsoup :: '
            f'{match=} :: '
            f'{name=} :: '
            f'{attrs=} :: '
            f'{recursive=} :: '
            f'{string=} :: '
            f'{limit=} :: '
            f'{case_sensitive=} :: '
            f'{kwargs=}'
        )

        # search both element as string and attribute text
        for element in elements:

            _places_to_search = [
                element.string,
                element.text,
                str(element),
            ]

            for _search in _places_to_search:

                if not _search:
                    continue

                logger.debug(
                    f'[SeleniumBrowser] :: find_anything_with_beautifulsoup :: searching :: '
                    f'{match=} :: '
                    f'search={_search[:100].encode()}'
                )

                _re_compile = re.compile(match)

                _re_search = _re_compile.search(_search)

                if _re_search:
                    logger.debug(
                        f'[SeleniumBrowser] :: find_anything_with_beautifulsoup :: '
                        f'found :: {match=} :: '
                        f'{_re_search.group()=} :: '
                        f'{_re_search.string=} :: '
                        f'{element=}'
                    )
                    if element not in MATCHES:
                        MATCHES.append(element)

        logger.info(f'[SeleniumBrowser] :: find_anything_with_beautifulsoup :: MATCHES :: {len(MATCHES)} found')
        return MATCHES

    def find_element(
            self,
            value: str,
            by: selenium.webdriver.common.by.By,
            **kwargs) -> selenium.webdriver.Chrome.find_element:
        """find element"""
        logger.debug(f'[SeleniumBrowser] :: find_element :: {self.current_url} :: {value=} :: {by=} :: {kwargs=}')

        find_element = self.webdriver.find_element(value=value, by=by, **kwargs)
        logger.debug(f'[SeleniumBrowser] :: find_element :: {self.current_url} :: {value=} :: found')

        logger.info(f'[SeleniumBrowser] :: find_element :: done')
        return find_element

    def find_elements(
            self,
            value: str,
            by: selenium.webdriver.common.by.By,
            caching: bool = False,
            **kwargs) -> list:
        """find elements"""
        logger.debug(f'[SeleniumBrowser] :: find_elements :: {self.current_url} :: {value=} :: {by=} :: {kwargs=}')

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
        logger.debug(f'[SeleniumBrowser] :: find_elements :: {len(find_elements)} elements found')

        logger.info(f'[SeleniumBrowser] :: find_elements :: done')
        return find_elements

    def find_elements_with_beautifulsoup(
            self,
            match: str,
            name: str = None,
            attrs: dict = {},
            recursive: bool = True,
            string: str = None,
            limit: int = None,
            case_sensitive: bool = False):

        # find all tags
        _bs_elements = self.find_anything_with_beautifulsoup(
            match=match,
            name=name,
            attrs=attrs,
            recursive=recursive,
            string=string,
            limit=limit,
            case_sensitive=case_sensitive)

        logger.debug(
            f'[SeleniumBrowser] :: '
            f'find_elements_with_beautifulsoup :: '
            f'{len(_bs_elements)} beautifulsoup elements'
        )

        elements = []

        _re_match = re.compile(match)

        if case_sensitive:
            _re_match = re.compile(match, re.IGNORECASE)

        for _bs_element in _bs_elements:

            if type(_bs_element) != bs4.element.Tag:
                continue

            _name = _bs_element.name

            for _attrs, _values in _bs_element.attrs.items():

                if not _values:
                    continue

                _attrs_list = [
                    'class',
                    'id',
                ]

                if _attrs not in _attrs_list:
                    continue

                if type(_values) == list:
                    _values = ' '.join(_values)

                _selenium_css_selector = f'{_name}[{_attrs}="{_values}"]'

                logger.debug(f'[SeleniumBrowser] :: find_elements_with_beautifulsoup :: {_selenium_css_selector=}')

                _selenium_elements = self.find_elements(by=self.by.CSS_SELECTOR, value=_selenium_css_selector)

                for _selenium_element in _selenium_elements:

                    _selenium_text = _selenium_element.text

                    if _re_match.search(_selenium_text):

                        if _selenium_element not in elements:
                            elements.append(_selenium_element)

            logger.debug(f'[SeleniumBrowser] :: find_elements_with_beautifulsoup :: {len(elements)} elements')
            logger.info(f'[SeleniumBrowser] :: find_elements_with_beautifulsoup :: done')

        return elements

    def find_xpath(
            self,
            value: str,
            by: selenium.webdriver.common.by.By = selenium.webdriver.common.by.By.XPATH,
            **kwargs) -> selenium.webdriver.Chrome.find_element:
        """find xpath"""
        logger.debug(f'[SeleniumBrowser] :: find_xpath :: {self.current_url} :: {value=} :: {by=} :: {kwargs=}')

        find_xpath = self.find_element(value=value, by=by, **kwargs)
        logger.debug(f'[SeleniumBrowser] :: find_xpath :: {self.current_url} :: {find_xpath=} :: found')

        logger.info(f'[SeleniumBrowser] :: find_xpath :: done')
        return find_xpath

    def get(self, url: str, **kwargs) -> bool:
        """get url"""
        logger.debug(f'[SeleniumBrowser] :: get :: {url} :: {kwargs=}')

        if not self.webdriver:
            raise Exception(f'[SeleniumBrowser] :: get :: failed :: missing webdriver')

        try:
            self.webdriver.get(url, **kwargs)

            logger.debug(
                f'[SeleniumBrowser] :: '
                f'get :: '
                f'{self.session_id=} :: '
                f'{url} :: '
                f'{self.current_url=} :: '
                f'{kwargs=}'
            )

            if self.config.cookies_autosave:
                self.autosaving_cookies()

            logger.info(f'[SeleniumBrowser] :: get :: done')
            return True

        except Exception as error:
            # traceback.print_exc()
            raise Exception(f'[SeleniumBrowser] :: get :: failed :: {error=}')

    def get_cookie(self, name: str) -> dict:
        """get cookie by name"""
        logger.debug(f'[SeleniumBrowser] :: get_cookie :: {name=}')
        get_cookie = self.webdriver.get_cookie(name=name)
        logger.debug(f'[SeleniumBrowser] :: get_cookie :: {get_cookie=}')
        logger.info(f'[SeleniumBrowser] :: get_cookie :: done')
        return get_cookie

    def get_cookies(self) -> [dict]:
        """get all cookies"""
        logger.debug(f'[SeleniumBrowser] :: get_cookies :: ')
        get_cookies = self.webdriver.get_cookies()
        logger.debug(f'[SeleniumBrowser] :: get_cookies :: {len(get_cookies)} total cookies')
        logger.info(f'[SeleniumBrowser] :: get_cookies :: done')
        return get_cookies

    def get_cookies_base64(self) -> str:
        """get cookies as base64"""
        logger.debug(f'[SeleniumBrowser] :: get_cookies_base64 ::')

        get_cookies_base64 = self.get_cookies()
        get_cookies_base64 = base64.b64encode(
            json.dumps(get_cookies_base64).encode()
        ).decode()
        logger.debug(f'[SeleniumBrowser] :: get_cookies_base64 :: {len(get_cookies_base64) / 1024} KB')

        logger.info(f'[SeleniumBrowser] :: get_cookies_base64 :: done')
        return get_cookies_base64

    def get_cookies_json(self) -> json.dumps:
        """get cookies as json"""
        logger.debug(f'[SeleniumBrowser] :: get_cookies_json ::')

        get_cookies_json = self.get_cookies()
        get_cookies_json = json.dumps(get_cookies_json)
        logger.debug(f'[SeleniumBrowser] :: get_cookies_json :: {len(get_cookies_json) / 1024} KB')

        logger.info(f'[SeleniumBrowser] :: get_cookies_json :: done')
        return get_cookies_json

    def get_cookies_summary(self) -> dict:
        """get cookies summary"""
        logger.debug(f'[SeleniumBrowser] :: get_cookies_summary ::')

        result = self.get_cookies()
        summary = {}
        if result:
            for cookie in result:
                cookie = dict(cookie)
                domain = cookie.get('domain')
                name = cookie.get('name')
                expiry = cookie.get('expiry')

                logger.debug(f'[SeleniumBrowser] :: get_cookies_summary :: {cookie}')
                logger.debug(f'[SeleniumBrowser] :: get_cookies_summary :: domain :: {domain}')
                logger.debug(f'[SeleniumBrowser] :: get_cookies_summary :: name :: {name}')
                logger.debug(f'[SeleniumBrowser] :: get_cookies_summary :: expiry :: {expiry}')

                if domain in summary.keys():
                    summary[domain].append(cookie)
                else:
                    summary[domain] = [cookie]

        logger.debug(f'[SeleniumBrowser] :: get_cookies_summary :: summary :: {summary}')
        logger.info(f'[SeleniumBrowser] :: get_cookies_summary ::')
        return summary

    def get_log(self, log_type: str) -> list:
        """Get logs for log type"""
        logger.debug(f'[SeleniumBrowser] :: get_log :: {log_type=}')
        get_log = self.webdriver.get_log(log_type)
        logger.info(f'[SeleniumBrowser] :: [SeleniumBrowser] :: get_log :: done')
        return get_log

    def get_logs(self) -> dict:
        """Get all logs

        you can only run this once
        afterwards the logs are cleared from the webdriver
        """
        logger.debug(
            f'[SeleniumBrowser] :: '
            f'get_logs :: '
            f'{len(self.webdriver.log_types)} types found :: '
            f'{self.webdriver.log_types}'
        )

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

            logger.debug(f'[SeleniumBrowser] :: get_logs :: {log_type} :: {len(self._logs[log_type])} logs')
            logger.info(f'[SeleniumBrowser] :: [SeleniumBrowser] :: get_logs :: {log_type} :: done')

        logger.debug(f'[SeleniumBrowser] :: get_logs :: {len(self._logs)} total logs')
        logger.info(f'[SeleniumBrowser] :: [SeleniumBrowser] :: get_logs :: done')
        return self._logs

    def get_log_browser(self) -> list:
        """Get browser logs"""
        logger.debug(f'[SeleniumBrowser] :: get_log_browser')
        logs = self.get_log('browser')
        logger.debug(f'[SeleniumBrowser] :: get_log_browser :: {len(logs)} logs')
        logger.info(f'[SeleniumBrowser] :: get_log_browser :: done')
        return logs

    def get_log_driver(self) -> list:
        """Get driver logs"""
        logger.debug(f'[SeleniumBrowser] :: get_log_driver')
        logs = self.get_log('driver')
        logger.debug(f'[SeleniumBrowser] :: get_log_driver :: {len(logs)} logs')
        logger.info(f'[SeleniumBrowser] :: get_log_driver :: done')
        return logs

    def get_log_performance(self) -> list:
        """Get performance logs"""
        logger.debug(f'[SeleniumBrowser] :: get_log_performance')
        logs = self.get_log('performance')
        logger.debug(f'[SeleniumBrowser] :: get_log_performance :: {len(logs)} logs')
        logger.info(f'[SeleniumBrowser] :: get_log_performance :: done')
        return logs

    def get_page(self, *args, **kwargs) -> bool:
        """alias to get"""
        logger.debug(f'[SeleniumBrowser] :: get_page :: {args=} :: {kwargs=}')
        return self.get(*args, **kwargs)

    def get_page_source(self) -> str:
        """get page source"""
        get_page_source = self.page_source
        logger.debug(f'[SeleniumBrowser] :: get_page_source :: {round(len(get_page_source) / 1024)} KB')
        logger.info(f'[SeleniumBrowser] :: get_page_source :: done')
        return get_page_source

    def get_page_source_pandas(self, html: str = None):
        """get page source read by pands"""
        if not html:
            html = self.page_source

        dataframes = pandas.read_html(html)
        logger.debug(f'[SeleniumBrowser] :: get_page_source_pandas :: {dataframes}')

        return dataframes

    def get_page_source_beautifulsoup(
            self,
            markup: str = None,
            features: str = 'lxml') -> BeautifulSoupClient.BeautifulSoup:
        """read page source with beautifulsoup"""

        if not markup:
            markup = self.get_page_source()

        logger.debug(
            f'[SeleniumBrowser] :: '
            f'get_page_source_beautifulsoup :: '
            f'{features=} :: {round(len(markup) / 1024)} KB'
        )

        get_page_source_beautifulsoup = BeautifulSoupClient().read_markup(
            markup=markup,
            features=features).bs
        logger.debug(
            f'[SeleniumBrowser] :: '
            f'get_page_source_beautifulsoup :: '
            f'{len(get_page_source_beautifulsoup)} lines'
        )

        logger.info(f'[SeleniumBrowser] :: get_page_source_beautifulsoup :: done')
        return get_page_source_beautifulsoup

    def get_random_user_agent(
            self,
            filter: list or str = None,
            case_sensitive: bool = False) -> str:
        """get a random user agent string"""
        logger.debug(f'[SeleniumBrowser] :: get_random_user_agent :: {filter=} :: {case_sensitive=}')

        get_random_user_agent = SeleniumUserAgentBuilder().get_windows()

        logger.debug(f'[SeleniumBrowser] :: get_random_user_agent :: {get_random_user_agent}')
        logger.info(f'[SeleniumBrowser] :: get_random_user_agent :: done')
        return get_random_user_agent

    def get_screenshot_as_base64(self, **kwargs):
        """screenshot as base64"""
        logger.debug(f'[SeleniumBrowser] :: get_screenshot_as_base64 :: ')
        get_screenshot_as_base64 = self.webdriver.get_screenshot_as_base64(**kwargs)
        logger.debug(
            f'[SeleniumBrowser] :: '
            f'get_screenshot_as_base64 :: '
            f'{round(len(get_screenshot_as_base64) / 1024)} KB'
        )
        logger.info(f'[SeleniumBrowser] :: get_screenshot_as_base64 :: done')
        return get_screenshot_as_base64

    def get_screenshot_as_file(
            self,
            filename: str = None,
            prefix: str = None,
            folder: str = None,
            **kwargs) -> bool:
        """alias to save_screenshot"""
        logger.debug(
            f'[SeleniumBrowser] :: '
            f'get_screenshot_as_file :: '
            f'{filename=} :: '
            f'{prefix=} :: '
            f'{folder=} :: '
            f'{kwargs=}'
        )

        get_screenshot_as_file = self.save_screenshot(
            filename=filename,
            prefix=prefix,
            folder=folder,
            **kwargs)

        logger.info(f'[SeleniumBrowser] :: get_screenshot_as_file :: done')
        return get_screenshot_as_file

    def get_screenshot_as_png(self, **kwargs):
        """screenshot as png"""
        logger.debug(f'[SeleniumBrowser] :: get_screenshot_as_png ::')
        get_screenshot_as_png = self.webdriver.get_screenshot_as_png(**kwargs)
        logger.debug(f'[SeleniumBrowser] :: get_screenshot_as_png :: {round(len(get_screenshot_as_png) / 1024)} KB')
        logger.info(f'[SeleniumBrowser] :: get_screenshot_as_png :: done')
        return get_screenshot_as_png

    def is_running(self) -> bool:
        """webdriver is running"""

        if self.webdriver:
            logger.info(f'[SeleniumBrowser] :: is running')
            return True
        logger.error(f'[SeleniumBrowser] :: is not running')
        return False

    @property
    def keys(self):
        """Set of special keys codes"""
        return selenium.webdriver.common.keys.Keys

    @property
    def logs(self):
        return self.get_logs()

    def load_cookies_for_current_url(self) -> bool:
        """load cookies from file for current url"""
        logger.debug(f'load_cookies_for_current_url :: ')

        filename = self._url_filename(url=self.url)
        logger.debug(f'load_cookies_for_current_url :: {filename=} :: {self.url=}')

        load_cookies_for_current_url = self.add_cookie_from_file(file=filename)
        logger.info(f'[SeleniumBrowser] :: load_cookies_for_current_url :: done')
        return load_cookies_for_current_url

    def open_file(self, file_path: str):
        """open local html file path"""
        logger.debug(f'open_file :: {file_path}')
        return self.get(f'file:///{file_path}')

    @property
    def page_source(self):
        return self.webdriver.page_source

    def quit(self) -> bool:
        """gracefully quit webdriver"""
        logger.debug(f'[SeleniumBrowser] :: quit')

        if self.webdriver:
            try:
                self.close()
                self.webdriver.quit()
                self.webdriver.stop_client()
            except Exception as error:
                message, session, stacktrace = self.error_parsing(error)
                logger.error(f'[SeleniumBrowser] :: quit :: failed :: {message=} :: {session=} :: {stacktrace=}')
                return False

        logger.info(f'[SeleniumBrowser] :: quit :: done')
        return True

    def refresh(self) -> None:
        """refresh the page"""
        logger.debug(f'[SeleniumBrowser] :: refresh :: {self.current_url=}')
        refresh = self.webdriver.refresh()
        logger.info(f'[SeleniumBrowser] :: refresh :: done')
        return refresh or True

    def run(self) -> bool:
        """run webdriver"""
        logger.debug(f'[SeleniumBrowser] :: run')

        try:
            run = self.config.run()
            logger.info(f'[SeleniumBrowser] :: run :: done')
            return run
        except Exception as error:
            traceback.print_exc()
            raise Exception(f'[SeleniumBrowser] :: run :: failed :: {error=}')

    def save_cookies_for_current_url(self) -> bool:
        """save cookies for current url"""
        logger.debug(f'[SeleniumBrowser] :: save_cookies_for_current_url :: ')

        filename = self._url_filename(url=self.url)
        save_cookies_for_current_url = self.save_cookies_to_file(file=filename)
        logger.debug(f'[SeleniumBrowser] :: save_cookies_for_current_url :: {self.current_url} :: {filename}')

        logger.info(f'[SeleniumBrowser] :: save_cookies_for_current_url :: done')
        return save_cookies_for_current_url

    def save_cookies_to_file(self, file: str) -> bool:
        """save cookies to file"""
        logger.debug(f'[SeleniumBrowser] :: save_cookies_to_file :: {file}')

        with open(file, 'w') as cookies:
            cookies.write(
                self.get_cookies_json()
            )

        if os.path.exists(file):
            logger.debug(
                f'[SeleniumBrowser] :: '
                f'save_cookies_to_file :: '
                f'{os.path.abspath(file)} :: '
                f'{os.stat(file).st_size} B'
            )
            logger.info(f'[SeleniumBrowser] :: save_cookies_to_file :: done')
            return True

        logger.error(f'[SeleniumBrowser] :: save_cookies_to_file :: failed :: {file=}')
        return False

    def save_page_to_file(
            self,
            filename: str = None,
            prefix: str = None,
            folder: str = None,
            **kwargs):
        """save page to file"""
        logger.debug(
            f'[SeleniumBrowser] :: '
            f'save_page_to_file :: '
            f'{self.current_url} :: '
            f'{filename=} :: '
            f'{prefix=} :: '
            f'{folder=} :: '
            f'{kwargs=}'
        )

        if not filename:
            filename = self._screenshot_name(prefix)
            logger.debug(f'[SeleniumBrowser] :: save_page_to_file :: {filename=}')

        if not folder:
            path = os.path.abspath(tempfile.gettempdir())
            logger.debug(f'[SeleniumBrowser] :: save_page_to_file :: {path=}')
        else:
            path = os.path.abspath(folder)
            logger.debug(f'[SeleniumBrowser] :: save_page_to_file :: {path=}')

        if not os.path.exists(path):
            os.makedirs(path)

        save = os.path.join(path, filename)

        if self.webdriver.save_screenshot(save, **kwargs):
            logger.debug(
                f'[SeleniumBrowser] :: '
                f'save_page_to_file :: '
                f'{save} :: '
                f'{round(os.stat(save).st_size / 1024)} KB'
            )
            logger.info(f'[SeleniumBrowser] :: save_page_to_file :: done')
            return True

        logger.error(f'[SeleniumBrowser] :: save_page_to_file :: failed')
        return False

    def save_screenshot(
            self,
            filename: str = None,
            prefix: str = None,
            folder: str = None,
            **kwargs) -> bool:
        """save screenshot to file"""
        logger.debug(
            f'[SeleniumBrowser] :: '
            f'save_screenshot :: '
            f'{self.current_url} :: '
            f'{filename=} :: '
            f'{prefix=} :: '
            f'{folder=} :: '
            f'{kwargs=}'
        )

        if not filename:
            filename = self._screenshot_name(prefix)
            logger.debug(f'[SeleniumBrowser] :: save_screenshot :: {filename=}')

        if not folder:
            path = os.path.abspath(automon.Tempfile.gettempdir())
            logger.debug(f'[SeleniumBrowser] :: save_screenshot :: {path=}')
        else:
            path = os.path.abspath(folder)
            logger.debug(f'[SeleniumBrowser] :: save_screenshot :: {path=}')

        if not os.path.exists(path):
            os.makedirs(path)

        save = os.path.join(path, filename)

        if self.webdriver.save_screenshot(save, **kwargs):
            logger.debug(f'[SeleniumBrowser] :: save_screenshot :: {save} :: {round(os.stat(save).st_size / 1024)} KB')
            logger.info(f'[SeleniumBrowser] :: save_screenshot :: done')
            return True

        logger.error(f'[SeleniumBrowser] :: save_screenshot :: failed')
        return False

    def _screenshot_name(self, prefix=None):
        """Generate a unique filename"""
        logger.debug(f'[SeleniumBrowser] :: _screenshot_name :: {prefix=}')

        title = self.webdriver.title
        url = self.current_url

        hostname = self.urlparse(url).hostname

        timestamp = Dates.filename_timestamp()
        hostname_ = Sanitation.ascii_numeric_only(hostname)
        title_ = Sanitation.ascii_numeric_only(title)

        logger.debug(f'[SeleniumBrowser] :: _screenshot_name :: {url=}')
        logger.debug(f'[SeleniumBrowser] :: _screenshot_name :: {timestamp=}')
        logger.debug(f'[SeleniumBrowser] :: _screenshot_name :: {title_=}')
        logger.debug(f'[SeleniumBrowser] :: _screenshot_name :: {hostname_=}')

        if prefix:
            prefix = Sanitation.safe_string(prefix)
            _screenshot_name = f'{prefix}_{timestamp}_{hostname_}_{title_}.png'
            logger.info(f'[SeleniumBrowser] :: _screenshot_name :: {_screenshot_name=}')
            return _screenshot_name

        _screenshot_name = f'{timestamp}_{hostname_}_{title_}.png'
        logger.debug(f'[SeleniumBrowser] :: _screenshot_name :: {_screenshot_name=}')

        logger.debug(f'[SeleniumBrowser] :: _screenshot_name :: done')
        return _screenshot_name

    @property
    def session_id(self):
        if self.webdriver:
            return self.config.webdriver_wrapper.session_id

    def set_window_size(self, width=1920, height=1080, device_type=None) -> bool:
        """set browser resolution"""
        logger.debug(f'[SeleniumBrowser] :: set_window_size :: {width=} :: {height=} :: {device_type=}')

        try:
            self.config.webdriver_wrapper.set_window_size(
                width=width,
                height=height,
                device_type=device_type)
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            logger.error(f'[SeleniumBrowser] :: set_window_size :: failed :: {message=} :: {session=} :: {stacktrace=}')
            return False

        logger.info(f'[SeleniumBrowser] :: set_window_size :: done')
        return True

    def set_window_position(self, x: int = 0, y: int = 0):
        """set browser position"""
        logger.debug(f'[SeleniumBrowser] :: set_window_position :: {x=} :: {y=}')
        set_window_position = self.webdriver.set_window_position(x, y)
        logger.info(f'[SeleniumBrowser] :: set_window_position :: done')
        return set_window_position

    def start(self):
        """alias to run"""
        return self.run()

    def switch_to_new_window_tab(self):
        """Opens a new tab and switches to new tab"""
        self.webdriver.switch_to.new_window('tab')
        logger.debug(f'[SeleniumBrowser] :: switch_to_new_window_tab :: {self.webdriver.current_window_handle=}')
        logger.info(f'[SeleniumBrowser] :: switch_to_new_window_tab :: done')
        return True

    def switch_to_new_window_window(self):
        """Opens a new window and switches to new window"""
        self.webdriver.switch_to.new_window('window')
        logger.debug(f'[SeleniumBrowser] :: switch_to_new_window_window :: {self.webdriver.current_window_handle=}')
        logger.info(f'[SeleniumBrowser] :: switch_to_new_window_window :: done')
        return True

    def upload_file(self, element: selenium.webdriver.remote.webelement.WebElement, file_path: str = None):
        logger.debug(f'[SeleniumBrowser] :: upload_file :: {file_path=} :: {element=} :: >>>>')

        # driver.find_element(By.CSS_SELECTOR, "input[type='file']")
        upload = element.send_keys(file_path)
        # driver.find_element(By.ID, "file-submit").click()
        logger.debug(f'[SeleniumBrowser] :: upload_file :: {upload=}')
        logger.info(f'[SeleniumBrowser] :: upload_file :: done')

        return upload

    @property
    def url(self):
        """alias to current_url"""
        return self.current_url

    def _url_filename(self, url: str):
        """turn url into a filename"""
        logger.debug(f'[SeleniumBrowser] :: _url_filename :: {url=}')

        parsed = self.urlparse(url)
        hostname = parsed.hostname
        cookie_file = f'cookies-{hostname}.json'

        logger.debug(f'[SeleniumBrowser] :: _url_filename :: {hostname=}')
        logger.debug(f'[SeleniumBrowser] :: _url_filename :: {cookie_file=}')

        logger.debug(f'[SeleniumBrowser] :: _url_filename :: done')
        return cookie_file

    @property
    def _urllib(self):
        return urllib

    def urlparse(self, url: str):
        """parse url"""
        logger.debug(f'[SeleniumBrowser] :: urlparse :: {url=}')
        parsed = urllib.parse.urlparse(url=url)
        logger.debug(f'[SeleniumBrowser] :: urlparse :: {parsed=}')
        logger.info(f'[SeleniumBrowser] :: urlparse :: done')
        return parsed

    @property
    def user_agent(self):
        try:
            return self.webdriver.execute_script("return navigator.userAgent")
        except:
            return None

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
            f'{timeout=} :: '
        )

        timeout_start = time.time()
        timeout_elapsed = round(abs(timeout_start - time.time()), 1)

        RESULT = []

        while timeout_elapsed < timeout:

            logger.debug(
                f'wait_for_anything :: '
                f'timeout {timeout_elapsed}/{timeout} sec :: '
                f'{self.current_url=} :: '
                f'{value=} :: '
                f'{by=}'
            )

            try:
                RESULT = self.find_anything(
                    match=match,
                    value=value,
                    value_attr=value_attr,
                    by=by,
                    case_sensitive=case_sensitive,
                    exact_match=exact_match,
                    return_first=return_first,
                    **kwargs)

                logger.debug(f'wait_for_anything :: {len(RESULT)} elements found')

                if RESULT:
                    logger.info(f'[SeleniumBrowser] :: wait_for_anything :: done')
                    return RESULT

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

        logger.error(f'[SeleniumBrowser] :: wait_for_anything :: failed :: {match=} :: {value=} :: {by=}')

        return []

    def wait_for_anything_with_beautifulsoup(
            self,
            match: str,
            name: str = None,
            attrs: dict = {},
            recursive: bool = True,
            string: str = None,
            limit: int = None,
            case_sensitive: bool = False,
            timeout: int = 30,
            **kwargs) -> list:
        """wait for anything with beautifulsoup"""

        logger.debug(
            f'wait_for_anything_with_beautifulsoup :: '
            f'{match=} :: '
            f'{timeout=} :: '
        )

        timeout_start = time.time()
        timeout_elapsed = round(abs(timeout_start - time.time()), 1)

        RESULT = []

        while timeout_elapsed < timeout:

            logger.debug(
                f'wait_for_anything_with_beautifulsoup :: '
                f'timeout {timeout_elapsed}/{timeout} sec :: '
                f'{self.current_url=} :: '
            )

            try:
                RESULT = self.find_anything_with_beautifulsoup(
                    match=match,
                    name=name,
                    attrs=attrs,
                    recursive=recursive,
                    string=string,
                    limit=limit,
                    case_sensitive=case_sensitive,
                    **kwargs)

                logger.debug(
                    f'wait_for_anything_with_beautifulsoup :: '
                    f'{len(RESULT)} elements found'
                )

                if RESULT:
                    logger.info(f'[SeleniumBrowser] :: wait_for_anything_with_beautifulsoup :: done')
                    return RESULT

            except Exception as error:
                logger.error(
                    f'wait_for_anything_with_beautifulsoup :: '
                    f'failed :: '
                    f'timeout {timeout_elapsed}/{timeout} sec :: '
                    f'{error=} :: '
                    f'{match=} :: '
                )

            timeout_elapsed = round(abs(timeout_start - time.time()), 1)

        return RESULT

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
                    logger.info(f'[SeleniumBrowser] :: wait_for_element :: done')
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

        logger.error(f'[SeleniumBrowser] :: wait_for_element :: failed :: {value=} :: {by=}')
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
                    logger.info(f'[SeleniumBrowser] :: wait_for_elements :: done')
                    return find

            except Exception as error:
                logger.error(f'[SeleniumBrowser] :: wait_for_elements :: failed :: {error=} :: {value=} :: {by=}')

            timeout_elapsed = round(abs(timeout_start - time.time()), 1)

        logger.error(f'[SeleniumBrowser] :: wait_for_elements :: failed :: {value=} :: {by=}')
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

        logger.info(f'[SeleniumBrowser] :: wait_for_id :: done')
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

        logger.info(f'[SeleniumBrowser] :: wait_for_xpath :: done')
        return wait_for_xpath

    @property
    def window_size(self):
        return self.config.webdriver_wrapper.window_size
