import re
import pandas
import random
import datetime
import statistics
import selenium.common.exceptions

import automon
import automon.integrations.seleniumWrapper
import automon.integrations.seleniumWrapper.proxies_public

from automon import log
from automon.helpers.sleeper import Sleeper
from automon.integrations.seleniumWrapper import SeleniumBrowser, ChromeWrapper

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


class FacebookGroups(object):
    _xpath_close_login_popup = '/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/div'
    _xpath_content_unavailable = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[1]/div[2]/div[1]/h2/span'
    _xpath_title = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[1]/div[2]/div/div/div/div/div[1]/div/div/div/div/div/div[1]/h1/span/a'
    _xpath_temporarily_blocked = '/html/body/div[1]/div[2]/div[1]/div/div/div[1]/div/div[2]'
    _xpath_must_login = '/html/body/div[1]/div[1]/div[1]/div/div[2]/div/div'
    _xpath_blocked_by_login = ''
    _xpath_browser_not_supported = ''

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

    BROWSER_HEADLESS = True

    RATE_LIMITING = False
    RATE_PER_MINUTE = 1
    RATE_COUNTER = []
    LAST_REQUEST = None
    WAIT_BETWEEN_RETRIES = random.choice(range(1, 60))

    PROXY_ENABLED = None
    PROXY_RANDOM = None
    PROXIES = []

    USER_AGENT_STRING: str = None
    USER_AGENT_RANDOM: bool = False

    PROXIES_WEIGHT = {
        'Connect to Wi-Fi': -0.25,
        "You’re Temporarily Blocked": 0.90,
        "You must log in to continue": 0.90,
        'ERR_TIMED_OUT': -0.5,
        'ERR_CERT_AUTHORITY_INVALID': -0.25,
        'ERR_CONNECTION_RESET': -0.25,
        'ERR_TUNNEL_CONNECTION_FAILED': -0.25,
        'ERR_EMPTY_RESPONSE': -0.25,
        'ERR_PROXY_CONNECTION_FAILED': -0.25,
    }

    PROXY = None

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

    def check_blocked_by_login(self):

        if self._check_blocked_by_login is not None:
            return self._check_blocked_by_login

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

        logger.debug(f'[FacebookGroups] :: {method} :: {element=}')
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

        logger.debug(f'[FacebookGroups] :: {method} :: {element=}')
        self._browser_not_supported = element
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

        logger.debug(f'[FacebookGroups] :: {method} :: {element=}')
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

        logger.debug(f'[FacebookGroups] :: {method} :: {element=}')
        self._content_unavailable = element
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

        logger.debug(f'[FacebookGroups] :: {method} :: {element=}')
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

        logger.debug(f'[FacebookGroups] :: {method} :: {element=}')
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
                'Created a year ago',
                'Created a week ago'
            ]

            for re_match in re_matches:

                element = self._browser.find_elements_with_beautifulsoup(
                    match=re_match,
                    name='span',
                    case_sensitive=True,
                )

                if element:
                    element = element[0].text
                    element = re.compile(re_match).match(element)[0]
                    break

            method = 'by SEARCH'

        logger.debug(f'[FacebookGroups] :: {method} :: {element=}')
        self._creation_date = element

        if not element:
            raise Exception(f'{element=}')

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

        if len(self.PROXIES) == 0:
            self.PROXIES = pandas.DataFrame(
                [dict(proxy=x, weight=0) for x in
                 automon.integrations.seleniumWrapper.proxies_public.proxy_filter_https_ips_and_ports()]
            )
            self.PROXIES = self.PROXIES.convert_dtypes()

        proxies = self.PROXIES

        # find a working proxy
        while True:

            if self.PROXY_RANDOM:
                proxies_weight_good = proxies[proxies.weight > 50]
                logger.debug(
                    f'[FacebookGroups] :: '
                    f'start :: '
                    f'PROXY LIST :: '
                    f'{len(proxies_weight_good)} proxies > 50'
                )

                if not proxies_weight_good.empty:
                    proxies_list = proxies_weight_good
                else:
                    proxies_top_quantile = proxies.sort_values(by='weight', ascending=False)
                    proxies_top_quantile = proxies_top_quantile[proxies_top_quantile.weight >= 0]
                    logger.debug(
                        f'[FacebookGroups] :: '
                        f'start :: '
                        f'PROXY LIST :: '
                        f'{len(proxies_top_quantile)} proxies >= 0'
                    )

                    if not proxies_top_quantile.empty:

                        proxies_list = proxies_top_quantile

                    else:
                        proxies_top_quantile = proxies.sort_values(by='weight', ascending=False)
                        proxies_top_quantile = proxies_top_quantile[
                            proxies_top_quantile['weight'] >= proxies_top_quantile['weight'].quantile(0.5)
                            ]
                        logger.debug(
                            f'[FacebookGroups] :: '
                            f'start :: '
                            f'PROXY LIST :: '
                            f'{len(proxies_top_quantile)} proxies >= 0.5 percentile:: '
                            f'{proxies_top_quantile=}')

                        proxies_list = proxies_top_quantile

                if len(proxies_list) < 2:
                    proxy = proxies.sample()
                else:
                    proxy = proxies_list.sample()

            if not self.PROXY_RANDOM:
                proxy = self.PROXIES.iloc[0]

            self._update_proxy(proxy=proxy, weight_multiplier=1.10)

            self._browser.config.webdriver_wrapper.enable_proxy(proxy['proxy'].item())
            logger.debug(f'[FacebookGroups] :: start :: proxy test :: {proxy.to_dict('records')[0]}')

            self._browser.run()
            try:
                self._browser.get(self.url)
            except Exception as error:
                logger.error(f'[FacebookGroups] :: start :: ERROR :: {self.url=} :: {error=}')
                pass

            for _proxy_error in self.PROXIES_WEIGHT.keys():
                search = self._browser.find_page_source_with_regex(_proxy_error)
                if search:
                    self._update_proxy(proxy=proxy, weight_multiplier=self.PROXIES_WEIGHT[_proxy_error])

                    logger.info(
                        f'[FacebookGroups] :: '
                        f'start :: '
                        f'PROXY FAILED :: '
                        f'{proxy.to_dict('records')[0]} :: '
                        f'{_proxy_error=}'
                    )
                    self.quit()
                    return self.start()

            self._update_proxy(proxy=proxy, weight_multiplier=1.10)
            logger.debug(f'[FacebookGroups] :: start :: PROXY FOUND :: {proxy.to_dict('records')[0]}')
            return True

        raise Exception(f'[FacebookGroups] :: _find_proxy :: ERROR :: no proxies worked ({len(self.PROXIES)} proxies)')

    def get(self, url: str) -> bool:
        """get url"""

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
            if len(proxy) > 0:
                proxy = self.PROXY.to_dict('records')[0]

        logger.info(
            f'[FacebookGroups] ::'
            f'get :: '
            f'{result=} :: '
            f'{proxy=} :: '
            f'{url} :: '
            f'{round(len(self._browser.webdriver.page_source) / 1024)} KB'
        )
        return result

    def get_about(self):
        """get about page"""

        result = self.get(url=self.url)
        about = self._browser._urllib.parse.urljoin(self.current_url + '/', 'about')
        result = self.get(url=about)

        logger.info(f'[FacebookGroups] :: {about} :: {result=}')

        return result

    def get_facebook_info(self, url: str = None) -> dict:
        logger.info(f'[FacebookGroups] :: get_facebook_info :: {url=}')

        self.reset_cache()

        self.set_url(url=url)

        self.get_about()
        self.check_close_login_popup()

        if self.check_blocked_by_login():
            return self.to_empty()

        if self.check_content_unavailable():
            return self.to_empty()

        if self.check_something_went_wrong():
            return self.to_empty()

        try:

            results = self.to_dict()
            logger.debug(f'[FacebookGroups] :: get_facebook_info :: {results=}')

            # increase weight
            if self.PROXY is not None:
                if len(self.PROXY) > 0:
                    self._update_proxy(proxy=self.PROXY, weight_multiplier=1.10)
                    logger.debug(
                        f'[FacebookGroups] :: '
                        f'get_facebook_info :: '
                        f'UPDATE PROXY :: '
                        f'{self.PROXY.to_dict('records')[0]}'
                    )

            return results

        except selenium.common.exceptions.WebDriverException as error:
            # quit old webdriver
            self.quit()

            # restart webdriver
            self.start(
                set_page_load_timeout=2
            )
            logger.info(f'[FacebookGroups] :: get_facebook_info :: error :: restarting :: {error}')
            return self.get_facebook_info(url=url)

        except Exception as error:
            import traceback
            # traceback.print_exc()
            # raise Exception(f'get_facebook_info :: error :: {error}')
            logger.info(f'[FacebookGroups] :: get_facebook_info :: error :: restarting :: {error}')

            # decrease weight
            if self.PROXY is not None:
                if len(self.PROXY) > 0:
                    self._update_proxy(proxy=self.PROXY, weight_multiplier=0.90)
                    logger.debug(
                        f'[FacebookGroups] :: '
                        f'get_facebook_info :: '
                        f'UPDATE PROXY :: '
                        f'{self.PROXY.to_dict('records')[0]}'
                    )

            # quit old webdriver
            self.quit()

            # restart webdriver
            self.start(
                set_page_load_timeout=2
            )

            return self.get_facebook_info(url=url)

    def get_with_rate_limiter(
            self,
            url: str,
            retry: int = 0,
            retries: int = 5,
            wait_between_retries: int = None,
            rate_per_minute: int = None,
    ) -> bool:
        """get with rate dynamic limit"""

        self.reset_cache()

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
        self.screenshot_error()
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

        logger.debug(f'[FacebookGroups] :: {method} :: {element=}')
        self._history = element

        if not element:
            Exception(f'{element=}')

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
        logger.debug(f'[FacebookGroups] :: set_url :: {self.url=}')
        return self.url

    def start(
            self,
            set_page_load_timeout: int = 2):
        """start new instance of selenium"""

        if self.PROXY is None and self.LAST_REQUEST is not None:
            pass

        self._browser.config.webdriver_wrapper = ChromeWrapper()

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
                return True

        else:

            logger.info(f'[FacebookGroups] :: start :: {self._browser}')
            logger.info(f'[FacebookGroups] :: start :: {self._browser}')
            browser = self._browser.run()
            self._browser.config.webdriver_wrapper.set_window_size(width=1920 * 0.60, height=1080)
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
            element = self._browser.find_all_with_beautifulsoup(
                string='[0-9]?+[,]?[0-9]+ total member[s]?',
                case_sensitive=True
            )
            if element:
                element = element[0].text

            method = 'by SEARCH'

        logger.debug(f'[FacebookGroups] :: {method} :: {element=}')
        self._members = element

        if not element:
            Exception(f'{element=}')

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

        logger.debug(f'[FacebookGroups] :: {method} :: {element=}')
        self._posts_monthly = element

        if not element:
            Exception(f'{element=}')

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

        logger.debug(f'[FacebookGroups] :: {method} :: {element=}')
        self._posts_today = element

        if not element:
            Exception(f'{element=}')

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

        logger.debug(f'[FacebookGroups] :: {method} :: {element=}')
        self._privacy = element

        if not element:
            Exception(f'{element=}')

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

        self._privacy_details = element
        logger.debug(f'[FacebookGroups] :: {method} :: {element=}')

        if not element:
            Exception(f'{element=}')

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
        return dict(
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

    def _update_proxy(self, proxy: pandas.DataFrame, weight_multiplier: int):

        if proxy['weight'].item() == 0:
            proxy['weight'] = proxy['weight'] + 1

        proxy['weight'] = proxy['weight'] * weight_multiplier
        proxy['weight'] = proxy['weight'].astype('int')
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

        logger.debug(f'[FacebookGroups] :: {method} :: {element=}')
        self._visible = element

        if not element:
            Exception(f'{element=}')

        return element
