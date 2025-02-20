import re
import pandas
import random
import hashlib
import datetime
import traceback
import statistics
import selenium.common.exceptions

import automon
import automon.integrations.seleniumWrapper
import automon.integrations.seleniumWrapper.proxies_public

from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO
from automon.helpers.sleeper import Sleeper
from automon.integrations.seleniumWrapper import SeleniumBrowser, ChromeWrapper

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


class FacebookGroups(object):
    _xpath_close_cookies_popup = '//*[@id="facebook"]/body/div[2]/div[1]/div/div[2]/div/div/div/div/div[2]/div/div[1]/div[2]/div/div[1]/div/span/span'
    _xpath_close_login_popup = '/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/div'
    _xpath_content_unavailable = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[1]/div[2]/div[1]/h2/span'
    _xpath_title = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[1]/div[2]/div/div/div/div/div[1]/div/div/div/div/div/div[1]/h1/span/a'
    _xpath_temporarily_blocked = '/html/body/div[1]/div[2]/div[1]/div/div/div[1]/div/div[2]'
    _xpath_must_login = '/html/body/div[1]/div[1]/div[1]/div/div[2]/div/div'
    _xpath_blocked_by_login = ''
    _xpath_browser_not_supported = ''
    _xpath_join_group = '//*[@id="mount_0_0_fq"]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div[2]/div/div/div[1]/div[2]/div/div/div/div/div[2]/div/div[1]/div/div/div/div/div[1]/div[2]/span/span'

    _xpath_creation_date = [
        '/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[3]/div/div/div/div/div/div[2]/div/div[3]/div/div/div[2]/div/div/span',
    ]
    _xpath_history = '/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[1]/div/div/div/div/div/div[2]/div[2]/div[3]/div/div/div[2]/div/div[2]/span/span'
    _xpath_members = [
        '/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[3]/div/div/div/div/div/div[2]/div/div[2]/div/div/div[2]/div/div[1]',
        '/html/body/div[1]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[3]/div/div/div/div/div/div[2]/div/div[2]/div/div/div[2]/div/div[1]/span',
        '//*[@id="mount_0_0_S5"]/div/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[3]/div/div/div/div/div/div[2]/div/div[2]/div/div/div[2]/div/div[1]/span',
    ]
    _xpath_posts_monthly = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[3]/div/div/div/div/div/div[2]/div/div[1]/div/div/div[2]/div/div[2]'
    _xpath_posts_today = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[3]/div/div/div/div/div/div[2]/div/div[1]/div/div/div[2]/div/div[1]'
    _xpath_privacy = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[1]/div/div/div/div/div/div[2]/div[2]/div[1]/div/div/div[2]/div/div[1]'
    _xpath_privacy_details = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[1]/div/div/div/div/div/div[2]/div[2]/div[1]/div/div/div[2]/div/div[2]'
    _xpath_visible = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[1]/div/div/div/div/div/div[2]/div[2]/div[2]/div/div/div[2]/div/div[1]'

    BROWSER_HEADLESS: bool = True

    RATE_LIMITING: bool = False
    RATE_PER_MINUTE: int = 1
    RATE_COUNTER: list = []
    LAST_REQUEST: int = None
    WAIT_BETWEEN_RETRIES: int = random.choice(range(1, 60))

    PROXY_ENABLED: bool = None
    PROXY_RANDOM: bool = None
    PROXIES: list = []

    USER_AGENT_STRING: str = None
    USER_AGENT_RANDOM: bool = False

    PROXIES_WEIGHT: dict = {
        'Connect to Wi-Fi': -0.25,
        "You’re Temporarily Blocked": 0.90,
        "You must log in to continue": 0.90,
        'ERR_TIMED_OUT': -0.5,
        'ERR_SSL_PROTOCOL_ERROR': -0.25,
        'ERR_CERT_AUTHORITY_INVALID': -0.25,
        'ERR_CONNECTION_RESET': -0.25,
        'ERR_TUNNEL_CONNECTION_FAILED': -0.25,
        'ERR_EMPTY_RESPONSE': -0.25,
        'ERR_PROXY_CONNECTION_FAILED': -0.25,
        'a7fe83ec64bb23eb28090598db3d166ed98e52e39d1afbbfd74c579553f93e4e': -0.25,
    }

    _PROXY: pandas.DataFrame = None

    def __init__(self, url: str = None):
        """Facebook Groups object

        Depends on Selenium"""
        self._url = url

        self._browser = SeleniumBrowser()

        self._content_unavailable = None
        self._creation_date = None
        self._creation_date_timestamp = None
        self._history = None
        self._members = None
        self._members_count = None
        self._posts_monthly = None
        self._posts_monthly_count = None
        self._posts_today = None
        self._posts_today_count = None
        self._privacy = None
        self._privacy_details = None
        self._title = None
        self._visible = None
        self._browser_not_supported = None

        self._check_blocked_by_login = None
        self._check_temporarily_blocked = None
        self._check_something_went_wrong = None
        self._check_page_loaded = None

    def average_rate(self):
        if self.RATE_COUNTER:
            avg_seconds = round(statistics.mean(self.RATE_COUNTER), 1)
            avg_minutes = round(avg_seconds / 60, 1)
            avg_hours = round(avg_minutes / 60, 1)
            logger.info(
                f'[FacebookGroups] :: '
                f'total requests={len(self.RATE_COUNTER)} :: '
                f'{avg_seconds=} :: '
                f'{avg_minutes=} :: '
                f'last request {self.RATE_COUNTER[-1]} sec')
            return avg_seconds
        return 0

    def checks(self) -> bool:
        self.check_close_cookies_popup()
        self.check_close_login_popup()

        if self.check_blocked_by_login():
            return True

        if self.check_content_unavailable():
            return True

        if self.check_something_went_wrong():
            return True

        if not self.check_page_loaded():
            return True

        return False

    def check_blocked_by_login(self):

        if self._check_blocked_by_login is not None:
            return self._check_blocked_by_login

        if 'login' in self.current_url:
            return f'{self.current_url}'

        element = self._browser.wait_for_xpath(value=self._xpath_blocked_by_login, timeout=0)
        if element:
            element = element.text

        method = 'by XPATH'

        if not element:
            element = self._browser.find_all_with_beautifulsoup(
                string='You must log in to continue.',
                case_sensitive=True
            )
            if element:
                element = element[0].text

            method = 'by SEARCH'

        logger.debug(f'[FacebookGroups] :: check_blocked_by_login :: {method} :: {element=}')
        self._blocked_by_login = element
        return element

    def check_browser_not_supported(self):

        if self._browser_not_supported is not None:
            return self._browser_not_supported

        element = self._browser.wait_for_xpath(
            value=self._xpath_browser_not_supported,
            timeout=0)
        if element:
            element = element.text

        method = 'by XPATH'

        if not element:
            element = self._browser.find_all_with_beautifulsoup(
                string='This browser is not supported',
                case_sensitive=True
            )
            if element:
                element = element[0].text

            method = 'by SEARCH'

        logger.debug(f'[FacebookGroups] :: check_browser_not_supported :: {method} :: {element=}')
        self._browser_not_supported = element
        return element

    def check_close_cookies_popup(self):
        element = self._browser.wait_for_xpath(value=self._xpath_close_cookies_popup, timeout=0)
        method = 'by XPATH'

        if not element:
            element = self._browser.find_anything(
                match='Close',
                value='[aria-label="Close"]',
                by=self._browser.by.CSS_SELECTOR,
            )
            if element:
                element = element[0]

            method = 'by SEARCH'

        if element:
            element.click()

        logger.debug(f'[FacebookGroups] :: check_close_cookies_popup :: {method} :: {element=}')
        return element

    def check_close_login_popup(self):
        element = self._browser.wait_for_xpath(value=self._xpath_close_login_popup, timeout=0)
        method = 'by XPATH'

        if not element:
            element = self._browser.find_anything(
                match='Close',
                value='[aria-label="Close"]',
                by=self._browser.by.CSS_SELECTOR,
            )
            if element:
                element = element[0]

            method = 'by SEARCH'

        if element:
            element.click()

        logger.debug(f'[FacebookGroups] :: check_close_login_popup :: {method} :: {element=}')
        return element

    def check_content_unavailable(self):
        """This content isn't available right now"""

        if self._content_unavailable is not None:
            return self._content_unavailable

        element = self._browser.wait_for_xpath(value=self._xpath_content_unavailable, timeout=0)
        if element:
            element = element.text
        method = 'by XPATH'

        if not element:
            element = self._browser.find_all_with_beautifulsoup(
                string="This content isn't available right now",
                case_sensitive=True
            )
            if element:
                element = element[0]

            method = 'by SEARCH'

        logger.debug(f'[FacebookGroups] :: check_content_unavailable :: {method} :: {element=}')
        self._content_unavailable = element
        return element

    def check_page_loaded(self):

        if self._check_page_loaded is not None:
            return self._check_page_loaded

        element = self._browser.wait_for_xpath(
            value=self._xpath_join_group,
            timeout=0)
        if element:
            element = element.text

        method = 'by XPATH'

        if not element:
            element = self._browser.find_anything_with_beautifulsoup(
                match='Join group',
                case_sensitive=True
            )
            if element:
                element = element[0].text

            method = 'by SEARCH'

        logger.debug(f'[FacebookGroups] :: check_page_loaded :: {method} :: {element=}')
        self._browser_not_supported = element
        return element

    def check_something_went_wrong(self):
        """Happens when facebook server has issues"""

        if self._check_something_went_wrong:
            return self._check_something_went_wrong

        element = self._browser.wait_for_anything_with_beautifulsoup(
            match='Sorry, something went wrong.',
            string='Sorry, something went wrong.',
            case_sensitive=True,
            timeout=0,
        )
        if element:
            element = element[0]

        method = 'by SEARCH'

        logger.debug(f'[FacebookGroups] :: check_something_went_wrong :: {method} :: {element=}')
        self._check_something_went_wrong = element
        return element

    def check_temporarily_blocked(self):
        """check if blocked by facebook"""

        if self._check_temporarily_blocked:
            return self._check_temporarily_blocked

        element = self._browser.wait_for_xpath(value=self._xpath_temporarily_blocked, timeout=0)
        method = 'by XPATH'
        if element:
            element = element.text

        if not element:
            re_matches = [
                "You.re Temporarily Blocked"
            ]

            for re_match in re_matches:

                elements = self._browser.find_elements_with_beautifulsoup(
                    match=re_match,
                    case_sensitive=True,
                )

                for element in elements:
                    element = element.text
                    element = re.compile(re_match).match(element)

                    if element:
                        element = element[0]
                        break

        logger.debug(f'[FacebookGroups] :: check_temporarily_blocked :: {method} :: {element=}')
        return element

    def creation_date(self):

        if self._creation_date is not None:
            return self._creation_date

        element = [
            x for x in
            [self._browser.wait_for_xpath(value=xpath, timeout=0) for xpath in self._xpath_creation_date] if x]
        if element:
            element = element[0].text
            element = element.splitlines()[0]
        method = 'by XPATH'

        if not element:
            re_matches = [
                r'Created \d+ year[s]? ago',
                r'Created \d+ week[s]? ago',
                r'Created on \d+ year[s]? ago',
                'Created a year ago',
                'Created a week ago'
            ]

            for re_match in re_matches:

                element = self._browser.find_anything_with_beautifulsoup(
                    match=re_match,
                    case_sensitive=True,
                )

                if element:
                    element = element[0].text
                    element = re.compile(re_match).match(element)[0]
                    break

            method = 'by SEARCH'

        logger.debug(f'[FacebookGroups] :: creation_date :: {method} :: {element=}')
        self._creation_date = element

        if not element:
            raise Exception(f'[FacebookGroups] :: creation_date :: {element=}')

        return element

    def creation_date_timestamp(self):

        if self._creation_date_timestamp is not None:
            return self._creation_date_timestamp

        if self._creation_date is not None or self.creation_date():
            # TODO: convert date to datetime timestamp
            logger.warn(NotImplemented)
            return

    @property
    def current_url(self):
        return self._browser.current_url

    def current_rate_too_fast(self):
        if self.average_rate() == 0:
            logger.info(f'[FacebookGroups] :: current_rate_too_fast :: False')
            return False

        if self.average_rate() < self.rate_per_minute:
            logger.info(f'[FacebookGroups] :: current_rate_too_fast :: True')
            return True

        return False

    @staticmethod
    def error_parsing(error, enable_stacktrace: bool = False) -> tuple:
        """parses selenium exeption error"""

        error_parsed = f'{error}'.splitlines()
        error_parsed = [f'{x}'.strip() for x in error_parsed]
        message = error_parsed[0]
        session = None
        stacktrace = None
        if len(error_parsed) > 1:
            session = error_parsed[1]
            stacktrace = error_parsed[2:]
            stacktrace = ' '.join(stacktrace)

        if enable_stacktrace:
            return message, session, stacktrace

        return message, session, 'disabled'

    def _find_proxy(self):
        logger.debug(f'[FacebookGroups] :: _find_proxy :: >>>>')

        if len(self.PROXIES) == 0:
            self.PROXIES = pandas.DataFrame(
                automon.integrations.seleniumWrapper.proxies_public.proxy_filter_ips_and_ports()
            )
            self.PROXIES['weight'] = 0
            self.PROXIES.columns = ['proxy', 'weight']
            self.PROXIES['weight'] = self.PROXIES['weight'].astype('float32')

        proxies = self.PROXIES

        # find a working proxy
        while True:

            if self.PROXY_RANDOM:
                quantile = proxies['weight'].quantile(0.5).item()
                proxies_list = proxies[proxies['weight'] >= quantile]
                logger.debug(
                    f'[FacebookGroups] :: '
                    f'_find_proxy :: '
                    f'proxy list :: '
                    f'{len(proxies_list)} proxies > {quantile=}'
                )

                if len(proxies_list) < 2:
                    proxy = proxies.sample()
                else:
                    proxy = proxies_list.sample()

            if not self.PROXY_RANDOM:
                proxy = self.PROXIES.iloc[0]

            self.PROXY = proxy
            self._update_proxy(proxy=proxy, weight_multiplier=1.10)

            self._browser.config.webdriver_wrapper.enable_proxy(proxy['proxy'].item())
            logger.debug(f'[FacebookGroups] :: _find_proxy :: proxy test :: {proxy.to_dict("records")[0]}')

            # self._browser.run()
            # try:
            #     self._browser.get('https://ip.oxylabs.io/')
            #     # self.get_about()
            # except Exception as error:
            #     # logger.error(f'[FacebookGroups] :: _find_proxy :: ERROR :: {self.url=} :: {error=}')
            #     pass
            #
            # for _proxy_error in self.PROXIES_WEIGHT:
            #
            #     search = self._browser.find_page_source_with_regex(_proxy_error)
            #     page_hash = hashlib.sha256(f'{self._browser.page_source}'.encode()).hexdigest()
            #
            #     if search or page_hash == _proxy_error:
            #         self._update_proxy(proxy=proxy, weight_multiplier=self.PROXIES_WEIGHT[_proxy_error])
            #
            #         logger.info(
            #             f'[FacebookGroups] :: '
            #             f'_find_proxy :: '
            #             f'proxy failed :: '
            #             f'{proxy.to_dict("records")[0]} :: '
            #             f'{_proxy_error=}'
            #         )
            #         self.quit()
            #         return self.start()

            # self._update_proxy(proxy=proxy, weight_multiplier=1.10)
            # logger.debug(f'[FacebookGroups] :: _find_proxy :: PROXY FOUND :: {proxy.to_dict("records")[0]}')
            return True

        raise Exception(f'[FacebookGroups] :: _find_proxy :: ERROR :: no proxies worked ({len(self.PROXIES)} proxies)')

    def get(self, url: str) -> bool:
        """get url"""
        logger.info(f'[FacebookGroups] :: get :: >>>>')

        self.reset_cache()

        now = datetime.datetime.now().timestamp()

        if self.LAST_REQUEST:
            seconds_elapsed_since_last_request = abs(self.LAST_REQUEST - now)
            self.RATE_COUNTER.append(round(seconds_elapsed_since_last_request, 1))
            self.LAST_REQUEST = round(now, 1)
        else:
            self.LAST_REQUEST = round(now, 1)

        if self.RATE_LIMITING:
            result = self.get_with_rate_limiter(url=url)
        else:
            result = self._browser.get(url=url)

        proxy = self.PROXY
        if proxy is not None:
            proxy = self.PROXY.to_dict("records")[0]

        logger.debug(
            f'[FacebookGroups] :: '
            f'get :: '
            f'{result=} :: '
            f'{proxy=} :: '
            f'{url} :: '
            f'{round(len(self._browser.webdriver.page_source) / 1024)} KB'
        )
        logger.info(f'[FacebookGroups] :: get :: done')

        return result

    def get_about(self):
        """get about page"""
        logger.debug(f'[FacebookGroups] :: get_about :: >>>>')

        # result = self.get(url=self.url)
        # about = self._browser._urllib.parse.urljoin(self.current_url + '/', 'about')
        about = self._browser._urllib.parse.urljoin(self.url + '/', 'about')
        result = self.get(url=about)

        logger.debug(f'[FacebookGroups] :: get_about :: {about=} :: {result=}')
        logger.info(f'[FacebookGroups] :: get_about :: done')

        return result

    def get_facebook_info(self, url: str = None) -> dict:
        logger.info(f'[FacebookGroups] :: get_facebook_info :: {url=} :: >>>>')

        self.set_url(url=url)

        # self.get(url=url)
        #
        # if self.checks():
        #     return self.to_empty()

        self.get_about()

        if self.checks():
            return self.to_empty()

        self.screenshot()

        results = self.to_dict()
        logger.debug(f'[FacebookGroups] :: get_facebook_info :: {results=}')

        # increase weight
        if self.PROXY:
            self._update_proxy(proxy=self.PROXY, weight_multiplier=1.10)
            logger.debug(
                f'[FacebookGroups] :: '
                f'get_facebook_info :: '
                f'UPDATE PROXY :: '
                f'{self.PROXY.to_dict("records")[0]}'
            )

        return results

    @property
    def PROXY(self):
        if self._PROXY is not None:
            if len(self._PROXY) > 0:
                return self._PROXY

    @PROXY.setter
    def PROXY(self, proxy: pandas.DataFrame):
        self._PROXY = proxy

    def get_with_rate_limiter(
            self,
            url: str,
            retry: int = 0,
            retries: int = 5,
            wait_between_retries: int = None,
            rate_per_minute: int = None,
    ) -> bool:
        """get with rate dynamic limit"""

        if wait_between_retries:
            self.WAIT_BETWEEN_RETRIES = wait_between_retries

        if rate_per_minute:
            self.RATE_PER_MINUTE = rate_per_minute

        result = None
        while retry < retries:

            if self.rate_limited():
                self.rate_limit_increase()
                Sleeper.seconds(seconds=self.WAIT_BETWEEN_RETRIES)
                logger.debug(
                    f'[FacebookGroups] :: '
                    f'get_with_rate_limiter :: '
                    f'retrying :: '
                    f'{url} :: '
                    f'{retry=} :: '
                    f'{retries=}'
                )
            else:
                self.rate_limit_decrease()

            result = self.get(url=url)
            logger.info(f'[FacebookGroups] :: get_with_rate_limiter :: {result}')
            return result

            retry = retry + 1

        logger.error(f'[FacebookGroups] :: get_with_rate_limiter :: error :: {url}')
        return result

    def quit(self):
        """quit selenium"""

        if self._browser:
            logger.info(f'[FacebookGroups] :: quit :: {self._browser=}')
            return self._browser.quit()

    @property
    def rate_per_minute(self) -> int:
        rate = int(60 / self.RATE_PER_MINUTE)
        return rate

    def history(self):

        if self._history is not None:
            return self._history

        element = self._browser.wait_for_xpath(value=self._xpath_history, timeout=0)
        if element:
            element = element.text
            if 'See more' in element:
                element = element.split('See more')
                element = element[0]
        method = 'by XPATH'

        if not element:
            re_matches = [
                r'Group created on \w+ \d+, \d+',
            ]

            for re_match in re_matches:

                elements = self._browser.find_elements_with_beautifulsoup(
                    match=re_match,
                    name='span',
                    case_sensitive=True,
                )

                if elements:

                    for element in elements:
                        element = element.text
                        element = re.compile(re_match).match(element)[0]

                        if element:
                            break

            method = 'by SEARCH'

        if not element:
            raise Exception(f'[FacebookGroups] :: history :: {element=}')

        logger.debug(f'[FacebookGroups] :: history :: {method} :: {element=}')
        self._history = element

        return element

    def rate_limit_decrease(self, multiplier: int = 0.75):
        before = self.WAIT_BETWEEN_RETRIES
        after = abs(int(self.WAIT_BETWEEN_RETRIES * multiplier))

        self.WAIT_BETWEEN_RETRIES = after

        if self.WAIT_BETWEEN_RETRIES == 0:
            self.WAIT_BETWEEN_RETRIES = 1

        logger.info(f'[FacebookGroups] :: {before=} :: {after=} :: {multiplier=}')
        return after

    def rate_limit_increase(self, multiplier: int = 2):
        if self.WAIT_BETWEEN_RETRIES == 0:
            self.WAIT_BETWEEN_RETRIES = random.choice(range(1, 60))

        before = self.WAIT_BETWEEN_RETRIES
        after = abs(int(self.WAIT_BETWEEN_RETRIES * multiplier))

        self.WAIT_BETWEEN_RETRIES = after

        logger.info(f'[FacebookGroups] :: {before=} :: {after=} :: {multiplier=}')
        return after

    def rate_limited(self):
        """rate limit checker"""

        if self.current_rate_too_fast():
            logger.info(f'[FacebookGroups] :: rate_limited :: True')
            return True

        if self.check_temporarily_blocked() or self.must_login():
            logger.info(f'[FacebookGroups] :: rate_limited :: True')
            return True

        logger.info(f'[FacebookGroups] :: rate_limited :: False')

        return False

    def reset_cache(self):
        self._content_unavailable = None
        self._creation_date = None
        self._creation_date_timestamp = None
        self._history = None
        self._members = None
        self._members_count = None
        self._posts_monthly = None
        self._posts_monthly_count = None
        self._posts_today = None
        self._posts_today_count = None
        self._privacy = None
        self._privacy_details = None
        self._title = None
        self._visible = None
        self._blocked_by_login = None
        self._browser_not_supported = None
        logger.info(f'[FacebookGroups] :: reset_cache :: done')

    def reset_rate_counter(self):
        self.RATE_COUNTER = []
        logger.info(f'[FacebookGroups] :: reset_rate_counter :: {self.RATE_COUNTER}')
        return self.RATE_COUNTER

    def restart(self):
        """quit and start new instance of selenium"""

        if self._browser:
            self.quit()
        logger.info(f'[FacebookGroups] :: restart :: {self._browser}')
        return self.start()

    def run(self):
        """run selenium browser"""

        if self._browser:
            logger.info(f'[FacebookGroups] :: run :: {self._browser}')
            return self._browser.run()

    def screenshot(self, filename: str = 'screenshot.png'):
        if self._browser.save_screenshot(filename=filename, folder='.'):
            logger.debug(f'[FacebookGroups] :: screenshot :: done')
            return True
        return False

    def screenshot_error(self):
        """get error screenshot"""

        if self.screenshot(filename='screenshot-error.png'):
            logger.debug(f'[FacebookGroups] :: screenshot_error :: done')
            return True
        return False

    def screenshot_success(self):
        """get success screenshot"""

        if self.screenshot(filename='screenshot-success.png'):
            logger.debug(f'[FacebookGroups] :: screenshot_success :: done')
            return True
        return False

    def set_url(self, url: str) -> str:
        """set new url"""

        self._url = url
        logger.debug(f'[FacebookGroups] :: set_url :: {url=}')
        return url

    def start(
            self,
            set_page_load_timeout: int = 2):
        """start new instance of selenium"""

        logger.debug(f'[FacebookGroups] :: start :: >>>>')

        if self.PROXY is None and self.LAST_REQUEST is not None:
            pass

        self._browser.config.webdriver_wrapper = ChromeWrapper()

        self._browser.config.webdriver_wrapper.enable_antibot_detection()

        # TOOD: missing this implementation
        # I think I deleted it somewhere
        self._browser.config.webdriver_wrapper.set_page_load_timeout = set_page_load_timeout

        if self.BROWSER_HEADLESS:
            self._browser.config.webdriver_wrapper.enable_headless()
            self._browser.config.webdriver_wrapper.set_locale_experimental()
        else:
            self._browser.config.webdriver_wrapper.set_locale_experimental()

        if self.USER_AGENT_RANDOM:
            self._browser.config.webdriver_wrapper.set_user_agent(
                self._browser.get_random_user_agent()
            )
        elif self.USER_AGENT_STRING:
            self._browser.config.webdriver_wrapper.set_user_agent(
                self.USER_AGENT_STRING
            )

        if self.PROXY_ENABLED:

            if self._find_proxy():
                browser = self._browser.run()
                logger.info(f'[FacebookGroups] :: start :: done')
                return True

        else:

            logger.debug(f'[FacebookGroups] :: start :: {self._browser}')
            browser = self._browser.run()
            self._browser.config.webdriver_wrapper.set_window_size(width=1920 * 0.60, height=1080)
            logger.info(f'[FacebookGroups] :: start :: done')
            return browser

    def stop(self):
        """alias to quit"""

        return self.quit()

    def members(self):

        if self._members is not None:
            return self._members

        for xpath in self._xpath_members:
            element = self._browser.wait_for_xpath(value=xpath, timeout=0)

            if element:
                element = element.text
                break

        method = 'by XPATH'

        if not element:
            regex = '[0-9]?+[,]?[0-9]+ total member[s]?'
            element = self._browser.find_all_with_beautifulsoup(
                string=regex,
                case_sensitive=True
            )
            if element:
                element = element[0].string
                element = re.search(regex, element)
                element = element.group()

            method = 'by SEARCH'

        if not element:
            raise Exception(f'[FacebookGroups] :: members :: {element=}')

        logger.debug(f'[FacebookGroups] :: members :: {method} :: {element=}')
        self._members = element

        return element

    def members_count(self):

        if self._members_count is not None:
            return self._members_count

        if self._members is not None or self.members():
            count = [x for x in self._members]
            count = [x for x in count if x in [str(x) for x in range(0, 10)]]
            if count:
                self._members_count = int(''.join(count)) if count else 0

                logger.debug(
                    f'[FacebookGroups] :: '
                    f'{self._members_count=}'
                )
                return self._members_count

    def must_login(self):
        element = self._browser.wait_for_xpath(self._xpath_must_login, timeout=0)
        method = 'by XPATH'
        if element:
            element = element.text
        logger.debug(f'[FacebookGroups] :: {method} :: {element=}')
        return element

    def posts_monthly(self):

        if self._posts_monthly is not None:
            return self._posts_monthly

        element = self._browser.wait_for_xpath(value=self._xpath_posts_monthly, timeout=0)
        if element:
            element = element.text
        method = 'by XPATH'

        if not element:
            element = self._browser.find_all_with_beautifulsoup(
                string='in the last month',
                case_sensitive=True
            )

            if element:
                element = element[0].text

            method = 'by SEARCH'

        if not element:
            raise Exception(f'[FacebookGroups] :: posts_monthly :: {element=}')

        logger.debug(f'[FacebookGroups] :: posts_monthly :: {method} :: {element=}')
        self._posts_monthly = element

        return element

    def posts_monthly_count(self):

        if self._posts_monthly_count is not None:
            return self._posts_monthly_count

        if self._posts_monthly is not None or self.posts_monthly():
            count = [x for x in self._posts_monthly]
            count = [x for x in count if x in [str(x) for x in range(0, 10)]]
            if count:
                self._posts_monthly_count = int(''.join(count)) if count else 0

                logger.debug(
                    f'[FacebookGroups] :: '
                    f'{self._posts_monthly_count=}'
                )
                return self._posts_monthly_count

    def posts_today(self):

        if self._posts_today is not None:
            return self._posts_today

        element = self._browser.wait_for_xpath(value=self._xpath_posts_today, timeout=0)
        if element:
            element = element.text
        method = 'by XPATH'

        if not element:
            element = self._browser.find_all_with_beautifulsoup(
                string='new post[s]? today',
                case_sensitive=True
            )
            if element:
                element = element[0].text

            method = 'by SEARCH'

        if not element:
            raise Exception(f'[FacebookGroups] :: posts_today :: {element=}')

        logger.debug(f'[FacebookGroups] :: posts_today :: {method} :: {element=}')
        self._posts_today = element

        return element

    def posts_today_count(self):

        if self._posts_today_count is not None:
            return self._posts_today_count

        if self._posts_today is not None or self.posts_today():
            count = [x for x in self._posts_today]
            count = [x for x in count if x in [str(x) for x in range(0, 10)]]
            if count:
                self._posts_today_count = int(''.join(count)) if count else 0

                logger.debug(
                    f'[FacebookGroups] :: '
                    f'{self._posts_today_count=}'
                )
                return self._posts_today_count

    def privacy(self):

        if self._privacy is not None:
            return self._privacy

        element = self._browser.wait_for_xpath(value=self._xpath_privacy, timeout=0)
        if element:
            element = element.text
        method = 'by XPATH'

        if not element:
            re_matches = [
                'Public',
                'Private',
                'Visible',
            ]

            for re_match in re_matches:
                element = self._browser.find_all_with_beautifulsoup(
                    name='span',
                    string=re_match,
                    case_sensitive=True
                )
                if element:
                    element = element[0].text
                    break

            method = 'by SEARCH'

        if not element:
            raise Exception(f'[FacebookGroups] :: privacy :: {element=}')

        logger.debug(f'[FacebookGroups] :: privacy :: {method} :: {element=}')
        self._privacy = element

        return element

    def privacy_details(self):

        if self._privacy_details is not None:
            return self._privacy_details

        element = self._browser.wait_for_xpath(value=self._xpath_privacy_details, timeout=0)
        if element:
            element = element.text
        method = 'by XPATH'

        if not element:
            re_matches = [
                "Anyone can see who's in the group and what they post.",
                "Only members can see who's in the group and what they post.",
            ]

            for re_match in re_matches:
                element = self._browser.find_all_with_beautifulsoup(
                    string=re_match,
                    case_sensitive=True
                )
                if element:
                    element = element[0].text
                    break

            method = 'by SEARCH'

        if not element:
            raise Exception(f'[FacebookGroups] :: privacy_details :: {element=}')

        self._privacy_details = element
        logger.debug(f'[FacebookGroups] :: privacy_details :: {method} :: {element=}')

        return element

    def title(self) -> str:

        if self._title is not None:
            return self._title

        self._title = self._browser.webdriver.title

        return_empty = [
            'Log into Facebook',
            'www.facebook.com'
        ]

        if self._title in return_empty:
            self._title = ''

        if self._title:
            self._title = self._title.split('|')
            self._title = self._title[0]
            self._title = self._title.strip()
        logger.debug(
            f'[FacebookGroups] :: '
            f'{self._title=}'
        )
        return self._title

    def to_dict(self):
        logger.debug(f'[FacebookGroups] :: to_dict :: >>>>')

        try:
            result = dict(
                creation_date=self.creation_date(),
                creation_date_timestamp=self.creation_date_timestamp(),
                history=self.history(),
                members=self.members(),
                members_count=self.members_count(),
                posts_monthly=self.posts_monthly(),
                posts_monthly_count=self.posts_monthly_count(),
                posts_today=self.posts_today(),
                posts_today_count=self.posts_today_count(),
                privacy=self.privacy(),
                privacy_details=self.privacy_details(),
                title=self.title(),
                url=self.url,
                visible=self.visible(),
                check_blocked_by_login=self.check_blocked_by_login(),
                check_browser_not_supported=self.check_browser_not_supported(),
                check_content_unavailable=self.check_content_unavailable(),
            )

        except Exception as error:
            traceback.print_exc()
            raise Exception(f'[FacebookGroups] :: to_dict :: ERROR :: {error=}')

        logger.info(f'[FacebookGroups] :: to_dict :: done')
        return result

    def to_empty(self):
        return dict(
            creation_date=None,
            creation_date_timestamp=None,
            history=None,
            members=None,
            members_count=None,
            posts_monthly=None,
            posts_monthly_count=None,
            posts_today=None,
            posts_today_count=None,
            privacy=None,
            privacy_details=None,
            title=None,
            url=self.url,
            visible=None,
            check_blocked_by_login=self.check_blocked_by_login(),
            check_browser_not_supported=self.check_browser_not_supported(),
            check_content_unavailable=self.check_content_unavailable(),
        )

    def _update_proxy(self, proxy: pandas.DataFrame, weight_multiplier: float):

        if proxy['weight'].item() == 0:
            proxy['weight'] = proxy['weight'] + 1

        proxy['weight'] = proxy['weight'] * weight_multiplier

        logger.debug(f'[FacebookGroups] :: _update_proxy :: {proxy.to_dict("records")[0]} :: {weight_multiplier=}')
        self.PROXIES.update(proxy)
        return self

    @property
    def url(self) -> str:
        return self.url_cleaner(self._url)

    @staticmethod
    def url_cleaner(url: str):
        """simple url cleaner"""

        if not url:
            return
        if url[-1] == '/':
            url = url[:-1]
        # https://m.facebook.com/groups/ -> https://www.facebook.com/groups/
        if '://m.' in url:
            url = url.replace('://m.', '://www.')
        return url

    def visible(self) -> str:

        if self._visible is not None:
            return self._visible

        element = self._browser.wait_for_xpath(value=self._xpath_visible, timeout=0)
        if element:
            element = element.text
        method = 'by XPATH'

        if not element:
            re_matches = [
                'Anyone can find this group.',
            ]

            for re_match in re_matches:
                element = self._browser.find_all_with_beautifulsoup(
                    string=re_match,
                    case_sensitive=True
                )
                if element:
                    element = element[0].text
                    break

            method = 'by SEARCH'

        if not element:
            raise Exception(f'[FacebookGroups] :: visible :: {element=}')

        logger.debug(f'[FacebookGroups] :: visible :: {method} :: {element=}')
        self._visible = element

        return element
