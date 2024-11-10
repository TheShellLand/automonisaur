import random
import datetime
import statistics

from automon import log
from automon.helpers.sleeper import Sleeper
from automon.integrations.seleniumWrapper import SeleniumBrowser, ChromeWrapper

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


class FacebookGroups(object):
    _xpath_popup_close = '/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/i'

    _xpath_content_unavailable = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[1]/div[2]/div[1]/span'

    _xpath_title = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[1]/div[2]/div/div/div/div/div[1]/div/div/div/div/div/div[1]/h1/span/a'

    _xpath_temporarily_blocked = '/html/body/div[1]/div[2]/div[1]/div/div/div[1]/div/div[2]'

    _xpath_must_login = '/html/body/div[1]/div[1]/div[1]/div/div[2]/div/div'

    _xpath_visible = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[1]/div/div/div/div/div/div[2]/div[3]/div/div/div[2]/div/div[2]/span/span'

    RATE_PER_MINUTE = 2
    RATE_COUNTER = []
    LAST_REQUEST = None
    WAIT_BETWEEN_RETRIES = random.choice(range(1, 60))

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
        self._blocked_by_login = None
        self._browser_not_supported = None

    def blocked_by_login(self):

        if self._blocked_by_login is not None:
            return self._blocked_by_login

        try:
            self._blocked_by_login = self._browser.wait_for_anything(
                match='You must log in to continue.',
                value='div',
                value_attr='text',
                by=self._browser.by.TAG_NAME,
                exact_match=True
            )
            if self._blocked_by_login:
                self._blocked_by_login = self._blocked_by_login[0]
                self._blocked_by_login = self._blocked_by_login.text
            logger.debug(self._blocked_by_login)
            return self._blocked_by_login
        except Exception as error:
            logger.error(error)

    def browser_not_supported(self):

        if self._browser_not_supported is not None:
            return self._browser_not_supported

        try:
            self._browser_not_supported = self._browser.wait_for_anything(
                match='This browser is not supported',
                value='div',
                value_attr='text',
                by=self._browser.by.TAG_NAME,
                exact_match=True
            )
            if self._browser_not_supported:
                self._browser_not_supported = self._browser_not_supported[0]
                self._browser_not_supported = self._browser_not_supported.text
                logger.debug(self._browser.user_agent)
            logger.debug(self._browser_not_supported)
            return self._browser_not_supported

        except Exception as error:
            logger.error(error)

    def close_login_popup(self):
        try:
            button = self._browser.find_anything(
                match='Close',
                value='[aria-label="Close"]',
                by=self._browser.by.CSS_SELECTOR,
            )

            if button:
                button[0].click()
            logger.debug(button)
        except Exception as error:
            logger.error(error)

    def content_unavailable(self):
        """This content isn't available right now"""

        if self._content_unavailable is not None:
            return self._content_unavailable

        try:
            self._content_unavailable = self._browser.wait_for_anything(
                match="This content isn't available right now",
                value='span',
                value_attr='text',
                by=self._browser.by.TAG_NAME,
                exact_match=True
            )
            if self._content_unavailable:
                self._content_unavailable = self._content_unavailable[0]
                self._content_unavailable = self._content_unavailable.text
            logger.debug(self._content_unavailable)
            return self._content_unavailable
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            logger.error(f'{self.url} :: {message=} :: {session=} :: {stacktrace=}')

    def creation_date(self):

        if self._creation_date is not None:
            return self._creation_date

        try:
            self._creation_date = self._browser.find_anything(
                match='Created',
                value='span',
                value_attr='text',
                by=self._browser.by.TAG_NAME,
                return_first=True
            )
            if self._creation_date:
                self._creation_date = self._creation_date[0]
                self._creation_date = self._creation_date.text.split('See more')[0]
                self._creation_date = self._creation_date.strip()
            logger.debug(self._creation_date)
            return self._creation_date
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            logger.error(f'{self.url} :: {message=} :: {session=} :: {stacktrace=}')

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
            logger.info(f'current_rate_too_fast :: False')
            return False

        if self.average_rate() < self.rate_per_minute:
            logger.info(f'current_rate_too_fast :: True')
            return True

        return False

    @property
    def rate_per_minute(self) -> int:
        rate = int(60 / self.RATE_PER_MINUTE)
        logger.info(f'{rate=} sec')
        return rate

    def average_rate(self):
        if self.RATE_COUNTER:
            seconds = round(statistics.mean(self.RATE_COUNTER), 1)
            minutes = round(seconds / 60, 1)
            hours = round(minutes / 60, 1)
            logger.info(f'total requests={len(self.RATE_COUNTER)} :: {seconds=} :: {minutes=}')
            return seconds
        return 0

    def history(self):

        if self._history is not None:
            return self._history

        try:
            self._history = self._browser.wait_for_anything(
                match='Group created',
                value='span',
                value_attr='text',
                by=self._browser.by.TAG_NAME,
                return_first=True
            )
            if self._history:
                self._history = self._history[0]
                self._history = self._history.text
                if 'See more' in self._history:
                    self._history = self._history.split('See more')
                    self._history = self._history[0]
            logger.debug(self._history)
            return self._history
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            logger.error(f'{self.url} :: {message=} :: {session=} :: {stacktrace=}')

    def temporarily_blocked(self):
        try:
            text = self._browser.wait_for_xpath(self._xpath_temporarily_blocked, timeout=5)
            if text:
                text = text.text
            logger.debug(text)
            return text
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            logger.error(f'{self.url} :: {message=} :: {session=} :: {stacktrace=}')

    def members(self):

        if self._members is not None:
            return self._members

        try:
            # TODO: need to clean up string from members and remove bad chars
            self._members = self._browser.wait_for_anything(
                match='total members',
                value='span',
                value_attr='text',
                by=self._browser.by.TAG_NAME,
                return_first=True
            )
            if self._members:
                self._members = self._members[0]
                self._members = self._members.text
            logger.debug(self._members)
            return self._members
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            logger.error(f'{self.url} :: {message=} :: {session=} :: {stacktrace=}')

    def members_count(self):

        if self._members_count is not None:
            return self._members_count

        if self._members is not None or self.members():
            count = [x for x in self._members]
            count = [x for x in count if x in [str(x) for x in range(0, 10)]]
            if count:
                self._members_count = int(''.join(count)) if count else 0

                logger.debug(self._members_count)
                return self._members_count

    def must_login(self):
        try:
            text = self._browser.wait_for_anything(self._xpath_must_login)
            if text:
                text = text.text
            logger.debug(text)
            return text
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            logger.error(f'{self.url} :: {message=} :: {session=} :: {stacktrace=}')

    def posts_monthly(self):

        if self._posts_monthly is not None:
            return self._posts_monthly

        try:
            self._posts_monthly = self._browser.wait_for_anything(
                match='in the last month',
                value='span',
                value_attr='text',
                by=self._browser.by.TAG_NAME,
                return_first=True
            )
            if self._posts_monthly:
                self._posts_monthly = self._posts_monthly[0]
                self._posts_monthly = self._posts_monthly.text
            logger.debug(self._posts_monthly)
            return self._posts_monthly
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            logger.error(f'{self.url} :: {message=} :: {session=} :: {stacktrace=}')

    def posts_monthly_count(self):

        if self._posts_monthly_count is not None:
            return self._posts_monthly_count

        if self._posts_monthly is not None or self.posts_monthly():
            count = [x for x in self._posts_monthly]
            count = [x for x in count if x in [str(x) for x in range(0, 10)]]
            if count:
                self._posts_monthly_count = int(''.join(count)) if count else 0

                logger.debug(self._posts_monthly_count)
                return self._posts_monthly_count

    def posts_today(self):

        if self._posts_today is not None:
            return self._posts_today

        try:
            self._posts_today = self._browser.wait_for_anything(
                match='new posts today',
                value='span',
                by=self._browser.by.TAG_NAME
            )
            if self._posts_today:
                self._posts_today = self._posts_today[-1]
                self._posts_today = self._posts_today.text
            logger.debug(self._posts_today)
            return self._posts_today
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            logger.error(f'{self.url} :: {message=} :: {session=} :: {stacktrace=}')

    def posts_today_count(self):

        if self._posts_today_count is not None:
            return self._posts_today_count

        if self._posts_today is not None or self.posts_today():
            count = [x for x in self._posts_today]
            count = [x for x in count if x in [str(x) for x in range(0, 10)]]
            if count:
                self._posts_today_count = int(''.join(count)) if count else 0

                logger.debug(self._posts_today_count)
                return self._posts_today_count

    def privacy(self):

        if self._privacy is not None:
            return self._privacy

        try:
            known_privacy = [
                'Public',
                'Private',
                'Visible',
            ]

            for privacy in known_privacy:
                self._privacy = self._browser.wait_for_anything(
                    match=privacy,
                    value='span',
                    by=self._browser.by.TAG_NAME,
                    exact_match=True,
                    return_first=True,
                )
                if self._privacy:
                    self._privacy = self._privacy[-1]
                    self._privacy = self._privacy.text
                    logger.debug(self._privacy)
                    return self._privacy
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            logger.error(f'{self.url} :: {message=} :: {session=} :: {stacktrace=}')

    def privacy_details(self):

        if self._privacy_details is not None:
            return self._privacy_details

        try:
            known_privacy_details = [
                "Anyone can see who's in the group and what they post.",
                "Only members can see who's in the group and what they post.",
            ]

            for privacy_details in known_privacy_details:
                self._privacy_details = self._browser.wait_for_anything(
                    match=privacy_details,
                    value='span',
                    by=self._browser.by.TAG_NAME,
                    exact_match=True
                )
                if self._privacy_details:
                    self._privacy_details = self._privacy_details[0]
                    self._privacy_details = self._privacy_details.text
                    logger.debug(self._privacy_details)
                    return self._privacy_details
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            logger.error(f'{self.url} :: {message=} :: {session=} :: {stacktrace=}')

    def title(self) -> str:

        if self._title is not None:
            return self._title

        try:
            self._title = self._browser.webdriver.title

            if 'Log into Facebook' in self._title:
                logger.error(self._title)
                return ''

            if self._title:
                self._title = self._title.split('|')
                self._title = self._title[0]
                self._title = self._title.strip()
            logger.debug(self._title)
            return self._title
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            logger.error(f'{self.url} :: {message=} :: {session=} :: {stacktrace=}')

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
        return url

    def visible(self) -> str:

        if self._visible is not None:
            return self._visible

        try:
            known_visible = [
                'Anyone can find this group.',
            ]

            for visible in known_visible:
                self._visible = self._browser.wait_for_anything(
                    match=visible,
                    value='span',
                    by=self._browser.by.TAG_NAME,
                    exact_match=True
                )
                if self._visible:
                    self._visible = self._visible[-1]
                    self._visible = self._visible.text
                    logger.debug(self._visible)
                    return self._visible
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            logger.error(f'{self.url} :: {message=} :: {session=} :: {stacktrace=}')

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

    def get(self, url: str) -> bool:
        """get url"""

        now = datetime.datetime.now().timestamp()

        if self.LAST_REQUEST:
            self.RATE_COUNTER.append(abs(round(self.LAST_REQUEST - now, 1)))
            self.LAST_REQUEST = round(now, 1)
        else:
            self.LAST_REQUEST = round(now, 1)

        result = self._browser.get(url=url)
        logger.info(f'{result=} :: {url} :: {round(len(self._browser.webdriver.page_source) / 1024)} KB')
        return result

    def get_about(self, rate_limiting: bool = True):
        """get about page"""
        url = f'{self.url}/about'

        if rate_limiting:
            result = self.get_with_rate_limiter(url=url)
        else:
            result = self.get(url=url)

        logger.info(f'{url} :: {result=}')

        return result

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
                logger.error(f'get_with_rate_limiter :: error :: {url} :: {retry=} :: {retries=}')
                continue
            else:
                self.rate_limit_decrease()

            result = self.get(url=url)
            logger.info(f'get_with_rate_limiter :: {result}')
            return result

            retry = retry + 1

        logger.error(f'get_with_rate_limiter :: error :: {url}')
        self.screenshot_error()
        return result

    def rate_limit_decrease(self, multiplier: int = 0.75):
        before = self.WAIT_BETWEEN_RETRIES
        after = abs(int(self.WAIT_BETWEEN_RETRIES * multiplier))

        self.WAIT_BETWEEN_RETRIES = after

        if self.WAIT_BETWEEN_RETRIES == 0:
            self.WAIT_BETWEEN_RETRIES = 1

        logger.info(f'{before=} :: {after=} :: {multiplier=}')
        return after

    def rate_limit_increase(self, multiplier: int = 2):
        if self.WAIT_BETWEEN_RETRIES == 0:
            self.WAIT_BETWEEN_RETRIES = random.choice(range(1, 60))

        before = self.WAIT_BETWEEN_RETRIES
        after = abs(int(self.WAIT_BETWEEN_RETRIES * multiplier))

        self.WAIT_BETWEEN_RETRIES = after

        logger.info(f'{before=} :: {after=} :: {multiplier=}')
        return after

    def rate_limited(self):
        """rate limit checker"""
        if self.current_rate_too_fast():
            logger.info(f'rate_limited :: True')
            return True

        if self.temporarily_blocked() or self.must_login():
            logger.info(f'rate_limited :: True')
            return True

        logger.error(f'rate_limited :: False')

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
        logger.info(f'reset_rate_counter :: {self.RATE_COUNTER}')
        return self.RATE_COUNTER

    def restart(self):
        """quit and start new instance of selenium"""
        if self._browser:
            self.quit()
        logger.info(f'restart :: {self._browser}')
        return self.start()

    def run(self):
        """run selenium browser"""
        if self._browser:
            logger.info(f'run :: {self._browser}')
            return self._browser.run()

    def screenshot(self, filename: str = 'screenshot.png'):
        if self._browser.save_screenshot(filename=filename, folder='.'):
            logger.debug(f'screenshot :: done')
            return True
        return False

    def screenshot_error(self):
        """get error screenshot"""
        if self.screenshot(filename='screenshot-error.png'):
            logger.debug(f'screenshot_error :: done')
            return True
        return False

    def screenshot_success(self):
        """get success screenshot"""
        if self.screenshot(filename='screenshot-success.png'):
            logger.debug(f'screenshot_success :: done')
            return True
        return False

    def set_url(self, url: str) -> str:
        """set new url"""
        self._url = url
        logger.debug(f'set_url :: {self.url=}')
        return self.url

    def start(self, headless: bool = True, random_user_agent: bool = False, set_user_agent: str = None):
        """start new instance of selenium"""
        self._browser.config.webdriver_wrapper = ChromeWrapper()

        if headless:
            self._browser.config.webdriver_wrapper.enable_headless()
            self._browser.config.webdriver_wrapper.set_locale_experimental()
        else:
            self._browser.config.webdriver_wrapper.set_locale_experimental()

        if random_user_agent:
            self._browser.config.webdriver_wrapper.set_user_agent(
                self._browser.get_random_user_agent()
            )
        elif set_user_agent:
            self._browser.config.webdriver_wrapper.set_user_agent(
                set_user_agent
            )

        logger.info(f'start :: {self._browser}')
        browser = self._browser.run()
        self._browser.config.webdriver_wrapper.set_window_size(width=1920 * 0.6, height=1080)
        return browser

    def stop(self):
        """alias to quit"""
        return self.quit()

    def to_dict(self):
        return dict(
            content_unavailable=self.content_unavailable(),
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
            blocked_by_login=self.blocked_by_login(),
            browser_not_supported=self.browser_not_supported(),
        )

    def to_empty(self):
        return dict(
            content_unavailable=self.content_unavailable(),
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
            blocked_by_login=None,
            browser_not_supported=None,
        )

    def quit(self):
        """quit selenium"""
        if self._browser:
            logger.info(f'quit :: {self._browser}')
            return self._browser.quit()
