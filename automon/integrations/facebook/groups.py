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
    WAIT_BETWEEN_RETRIES = random.choice(range(1, 60))

    def __init__(self, url: str = None):
        """Facebook Groups object

        Depends on Selenium"""
        self._url = url

        self._browser = SeleniumBrowser()

    def close_login_popup(self):
        try:
            button = self._browser.find_anything(
                match='Close',
                value='[aria-label="Close"]',
                by=self._browser.by.CSS_SELECTOR,
            )
            button[0].click()
        except Exception as error:
            logger.error(error)

    def content_unavailable(self):
        """This content isn't available right now"""

        try:
            text = self._browser.wait_for_xpath(self._xpath_content_unavailable, timeout=5)
            if text:
                text = text.text
            logger.debug(text)
            return text
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            logger.error(f'{self.url} :: {message=} :: {session=} :: {stacktrace=}')

    def creation_date(self):

        try:
            text = self._browser.find_anything(
                match='Created',
                value='span',
                by=self._browser.by.TAG_NAME
            )
            if text:
                text = text[0]
                text = text.text.split('See more')[0]
                text = text.strip()
            logger.debug(text)
            return text
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            logger.error(f'{self.url} :: {message=} :: {session=} :: {stacktrace=}')

    def creation_date_timestamp(self):
        if self.creation_date():
            # TODO: convert date to datetime timestamp
            return

    @property
    def current_url(self):
        return self._browser.current_url

    def current_rate_too_fast(self):
        if self.average_rate() == 0 or len(self.RATE_COUNTER) < 2:
            logger.info(f'current_rate_too_fast :: False')
            return False

        if self.average_rate() < self.rate_per_minute():
            logger.info(f'current_rate_too_fast :: True')
            return True

        return False

    def rate_per_minute(self) -> int:
        rate = int(60 / self.RATE_PER_MINUTE)
        logger.info(f'{rate=} sec')
        return rate

    def average_rate(self):
        if self.RATE_COUNTER:
            rate = int(statistics.mean(self.RATE_COUNTER))
            logger.info(f'{rate=} sec')
            return rate
        return 0

    def history(self):

        try:
            text = self._browser.wait_for_anything(
                match='Group created',
                value='span',
                by=self._browser.by.TAG_NAME
            )
            if text:
                text = text[-1]
                text = text.text
                if 'See more' in text:
                    text = text.split('See more')
                    text = text[0]
            logger.debug(text)
            return text
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

        try:
            # TODO: need to clean up string from members and remove bad chars
            text = self._browser.wait_for_anything(
                match='total members',
                value='span',
                by=self._browser.by.TAG_NAME
            )
            if text:
                text = text[-1]
                text = text.text
            logger.debug(text)
            return text
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            logger.error(f'{self.url} :: {message=} :: {session=} :: {stacktrace=}')

    def members_count(self):

        if self.members():
            count = [x for x in self.members()]
            count = [x for x in count if x in [str(x) for x in range(0, 10)]]
            if count:
                members_count = int(''.join(count)) if count else 0

                logger.debug(members_count)
                return members_count

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

        try:
            text = self._browser.wait_for_anything(
                match='in the last month',
                value='span',
                by=self._browser.by.TAG_NAME
            )
            if text:
                text = text[-1]
                text = text.text
            logger.debug(text)
            return text
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            logger.error(f'{self.url} :: {message=} :: {session=} :: {stacktrace=}')

    def posts_monthly_count(self):

        if self.posts_monthly():
            count = [x for x in self.posts_monthly()]
            count = [x for x in count if x in [str(x) for x in range(0, 10)]]
            if count:
                posts_monthly_count = int(''.join(count)) if count else 0

                logger.debug(posts_monthly_count)
                return posts_monthly_count

    def posts_today(self):

        try:
            text = self._browser.wait_for_anything(
                match='new posts today',
                value='span',
                by=self._browser.by.TAG_NAME
            )
            if text:
                text = text[-1]
                text = text.text
            logger.debug(text)
            return text
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            logger.error(f'{self.url} :: {message=} :: {session=} :: {stacktrace=}')

    def posts_today_count(self):

        if self.posts_today():
            count = [x for x in self.posts_today()]
            count = [x for x in count if x in [str(x) for x in range(0, 10)]]
            if count:
                posts_today_count = int(''.join(count)) if count else 0

                logger.debug(posts_today_count)
                return posts_today_count

    def privacy(self):

        try:
            known_privacy = [
                'Public',
                'Private',
                'Visible',
            ]

            for privacy in known_privacy:
                text = self._browser.wait_for_anything(
                    match=privacy,
                    value='span',
                    by=self._browser.by.TAG_NAME,
                    exact_match=True,
                    return_first=True,
                )
                if text:
                    text = text[-1]
                    text = text.text
                    logger.debug(text)
                    return text
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            logger.error(f'{self.url} :: {message=} :: {session=} :: {stacktrace=}')

    def privacy_details(self):

        try:
            known_privacy_details = [
                "Anyone can see who's in the group and what they post.",
                "Only members can see who's in the group and what they post.",
            ]

            for privacy_details in known_privacy_details:
                text = self._browser.wait_for_anything(
                    match=privacy_details,
                    value='span',
                    by=self._browser.by.TAG_NAME,
                    exact_match=True
                )
                if text:
                    text = text[0]
                    text = text.text
                    logger.debug(text)
                    return text
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            logger.error(f'{self.url} :: {message=} :: {session=} :: {stacktrace=}')

    def title(self) -> str:

        try:
            text = self._browser.webdriver.title

            if 'Log into Facebook' in text:
                logger.error(text)
                return ''

            if text:
                text = text.split('|')
                text = text[0]
                text = text.strip()
            logger.debug(text)
            return text
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

        try:
            known_visible = [
                'Anyone can find this group.',
            ]

            for visible in known_visible:
                text = self._browser.wait_for_anything(
                    match=visible,
                    value='span',
                    by=self._browser.by.TAG_NAME,
                    exact_match=True
                )
                if text:
                    text = text[-1]
                    text = text.text
                    logger.debug(text)
                    return text
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

        start = datetime.datetime.now().timestamp()

        result = self._browser.get(url=url)
        logger.info(f'{url} :: {result}')

        end = datetime.datetime.now().timestamp()
        seconds_elapsed = int(end - start)

        logger.info(f'{seconds_elapsed=} :: {result=}')
        self.RATE_COUNTER.append(seconds_elapsed)

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

        result = None
        while retry < retries:

            if self.rate_limited():
                self.rate_limit_increase()

                self.RATE_COUNTER.append(self.WAIT_BETWEEN_RETRIES)
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

    def run(self):
        """run selenium browser"""
        if self._browser:
            logger.info(f'run :: {self._browser}')
            return self._browser.run()

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
        )

    def quit(self):
        """quit selenium"""
        if self._browser:
            logger.info(f'quit :: {self._browser}')
            return self._browser.quit()
