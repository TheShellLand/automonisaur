import random
import datetime
import statistics

from automon.log import logger
from automon.helpers.sleeper import Sleeper
from automon.integrations.seleniumWrapper import SeleniumBrowser
from automon.integrations.seleniumWrapper.config_webdriver_chrome import ChromeWrapper

log = logger.logging.getLogger(__name__)
log.setLevel(logger.DEBUG)


class FacebookGroups(object):
    _xpath_about = [
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[3]/div/div/div/div/div/div/div[1]/div/div/div/div/div[2]/a[1]/div[1]/span',
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[3]/div/div/div/div/div/div/div[1]/div/div/div/div/div[1]/div[1]/span',
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[1]/div/div/div/div/div/div[2]/div[1]',
    ]
    _xpath_popup_close = [
        '/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/i',
    ]
    _xpath_content_unavailble = [
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[1]/div[2]/div[1]/span',
    ]
    _xpath_creation_date = [
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div[2]/div/div/div[4]/div/div/div/div/div/div[3]/div/div/div/div/div/div[2]/div/div[3]/div/div/div[2]/div/div/span',
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[3]/div/div/div/div/div/div[2]/div/div[3]/div/div/div[2]/div/div/span',
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[3]/div/div/div/div/div/div[2]/div/div[3]/div/div/div[2]/div/div/span',
    ]
    _xpath_history = [
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[1]/div/div/div/div/div/div[2]/div[4]/div/div/div[2]/div/div[2]/span/span',
    ]
    _xpath_title = [
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[1]/div[2]/div/div/div/div/div[1]/div/div/div/div/div/div[1]/h1/span/a',
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[1]/div[2]/div/div/div/div/div[1]/div/div/div/div/div/div[1]/h1/span/a',
    ]
    _xpath_temporarily_blocked = [
        '/html/body/div[1]/div[2]/div[1]/div/div/div[1]/div/div[2]/h2',
        '/html/body/div[1]/div[2]/div[1]/div/div/div[1]/div/div[2]',
    ]
    _xpath_members = [
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div[2]/div/div/div[4]/div/div/div/div/div/div[3]/div/div/div/div/div/div[2]/div/div[2]/div/div/div[2]/div/div[1]/span',
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[3]/div/div/div/div/div/div[2]/div/div[2]/div/div/div[2]/div/div[1]/span',
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[3]/div/div/div/div/div/div[2]/div/div[2]/div/div/div[2]/div/div[1]/span',
    ]
    _xpath_must_login = [
        '/html/body/div[1]/div[1]/div[1]/div/div[2]/div/div',
    ]
    _xpath_posts_today = [
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[3]/div/div/div/div/div/div[2]/div/div[1]/div/div/div[2]/div/div[1]/span',
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[3]/div/div/div/div/div/div[2]/div/div[1]/div/div/div[2]/div/div[1]/span',
    ]
    _xpath_posts_monthly = [
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[3]/div/div/div/div/div/div[2]/div/div[1]/div/div/div[2]/div/div[2]/span',
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[3]/div/div/div/div/div/div[2]/div/div[1]/div/div/div[2]/div/div[2]/span',
    ]
    _xpath_privacy = [
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[1]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div/div[1]/span/span',
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[1]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div/div[1]/span/span',
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[1]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div/div[1]/span/span',
    ]
    _xpath_privacy_details = [
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[1]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div/div[2]/span/span',
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[1]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div/div[2]/span/span',
    ]
    _xpath_visible = [
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[1]/div/div/div/div/div/div[2]/div[3]/div/div/div[2]/div/div[2]/span/span',
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[1]/div/div/div/div/div/div[2]/div[3]/div/div/div[2]/div/div[2]/span/span',
    ]

    def __init__(self, url: str = None):
        """Facebook Groups object

        Depends on Selenium"""
        self._url = url

        self._browser = SeleniumBrowser()

        self._rate_per_minute = 2
        self._rate_counter = []
        self._wait_between_retries = random.choice(range(1, 60))

    def content_unavailable(self):
        """This content isn't available right now"""

        try:
            xpath_content_unavailble = self._browser.wait_for_xpath(self._xpath_content_unavailble)
            content_unavailable = self._browser.find_xpath(xpath_content_unavailble).text
            log.debug(content_unavailable)
            return content_unavailable
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            log.error(str(dict(
                url=self.url,
                message=message,
                session=session,
                stacktrace=stacktrace,
            )))
            self.screenshot_error()

    def creation_date(self):

        try:
            xpath_creation_date = self._browser.wait_for_xpath(self._xpath_creation_date)
            creation_date = self._browser.find_xpath(xpath_creation_date).text
            log.debug(creation_date)
            return creation_date
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            log.error(str(dict(
                url=self.url,
                message=message,
                session=session,
                stacktrace=stacktrace,
            )))
            self.screenshot_error()

    def creation_date_timestamp(self):
        if self.creation_date():
            # TODO: convert date to datetime timestamp
            return

    def current_rate_too_fast(self):
        if self.average_rate() == 0 or len(self._rate_counter) < 2:
            log.info(False)
            return False

        if self.average_rate() < self.rate_per_minute():
            log.info(True)
            return True

        return False

    def rate_per_minute(self) -> int:
        rate = int(60 / self._rate_per_minute)
        log.info(str(dict(
            seconds=rate,
        )))
        return rate

    def average_rate(self):
        if self._rate_counter:
            rate = int(statistics.mean(self._rate_counter))
            log.info(str(dict(
                seconds=rate,
            )))
            return rate
        return 0

    def history(self):

        try:
            xpath_history = self._browser.wait_for_xpath(self._xpath_history)
            history = self._browser.find_xpath(xpath_history).text
            log.debug(history)
            return history
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            log.error(str(dict(
                url=self.url,
                message=message,
                session=session,
                stacktrace=stacktrace,
            )))
            self.screenshot_error()

    def temporarily_blocked(self):
        try:
            xpath_temporarily_blocked = self._browser.wait_for_xpath(
                self._xpath_temporarily_blocked
            )
            temporarily_blocked = self._browser.find_xpath(
                xpath_temporarily_blocked
            ).text
            log.debug(temporarily_blocked)
            return temporarily_blocked
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            log.error(str(dict(
                url=self.url,
                message=message,
                session=session,
                stacktrace=stacktrace,
            )))
            self.screenshot_error()

    def members(self):

        try:
            xpath_members = self._browser.wait_for_xpath(self._xpath_members)
            members = self._browser.find_xpath(xpath_members).text
            log.debug(members)
            return members
            # TODO: need to clean up string from members and remove bad chars
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            log.error(str(dict(
                url=self.url,
                message=message,
                session=session,
                stacktrace=stacktrace,
            )))
            self.screenshot_error()

    def members_count(self):

        if self.members():
            count = [x for x in self.members()]
            count = [x for x in count if x in [str(x) for x in range(0, 10)]]
            if count:
                members_count = int(''.join(count)) if count else 0

                log.debug(members_count)
                return members_count

    def must_login(self):
        try:
            xpath_must_login = self._browser.wait_for_xpath(
                self._xpath_must_login
            )
            must_login = self._browser.find_xpath(
                xpath_must_login
            ).text
            log.debug(must_login)
            return must_login
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            log.error(str(dict(
                url=self.url,
                message=message,
                session=session,
                stacktrace=stacktrace,
            )))
            self.screenshot_error()

    def posts_monthly(self):

        try:
            xpath_monthly_posts = self._browser.wait_for_xpath(self._xpath_posts_monthly)
            posts_monthly = self._browser.find_xpath(xpath_monthly_posts).text
            log.debug(posts_monthly)
            return posts_monthly
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            log.error(str(dict(
                url=self.url,
                message=message,
                session=session,
                stacktrace=stacktrace,
            )))
            self.screenshot_error()

    def posts_monthly_count(self):

        if self.posts_monthly():
            count = [x for x in self.posts_monthly()]
            count = [x for x in count if x in [str(x) for x in range(0, 10)]]
            if count:
                posts_monthly_count = int(''.join(count)) if count else 0

                log.debug(posts_monthly_count)
                return posts_monthly_count

    def posts_today(self):

        try:
            xpath_posts_today = self._browser.wait_for_xpath(self._xpath_posts_today)
            posts_today = self._browser.find_xpath(xpath_posts_today).text
            log.debug(posts_today)
            return posts_today
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            log.error(str(dict(
                url=self.url,
                message=message,
                session=session,
                stacktrace=stacktrace,
            )))
            self.screenshot_error()

    def posts_today_count(self):

        if self.posts_today():
            count = [x for x in self.posts_today()]
            count = [x for x in count if x in [str(x) for x in range(0, 10)]]
            if count:
                posts_today_count = int(''.join(count)) if count else 0

                log.debug(posts_today_count)
                return posts_today_count

    def privacy(self):

        try:
            xpath_privacy = self._browser.wait_for_xpath(self._xpath_privacy)
            privacy = self._browser.find_xpath(xpath_privacy).text
            log.debug(privacy)
            return privacy
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            log.error(str(dict(
                url=self.url,
                message=message,
                session=session,
                stacktrace=stacktrace,
            )))
            self.screenshot_error()

    def privacy_details(self):

        try:
            xpath_privacy_details = self._browser.wait_for_xpath(self._xpath_privacy_details)
            privacy_details = self._browser.find_xpath(xpath_privacy_details).text
            log.debug(privacy_details)
            return privacy_details
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            log.error(str(dict(
                url=self.url,
                message=message,
                session=session,
                stacktrace=stacktrace,
            )))
            self.screenshot_error()

    def title(self) -> str:

        try:
            xpath_title = self._browser.wait_for_xpath(self._xpath_title)
            title = self._browser.find_xpath(xpath_title).text
            log.debug(title)
            return title
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            log.error(str(dict(
                url=self.url,
                message=message,
                session=session,
                stacktrace=stacktrace,
            )))
            self.screenshot_error()

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
            xpath_visible = self._browser.wait_for_xpath(self._xpath_visible)
            visible = self._browser.find_xpath(xpath_visible).text
            log.debug(visible)
            return visible
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            log.error(str(dict(
                url=self.url,
                message=message,
                session=session,
                stacktrace=stacktrace,
            )))
            self.screenshot_error()

    @staticmethod
    def error_parsing(error, enabble_stacktrace: bool = False) -> tuple:
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

        if enabble_stacktrace:
            return message, session, stacktrace

        return message, session, 'disabled'

    def get(self, url: str) -> bool:
        """get url"""

        start = datetime.datetime.now().timestamp()

        result = self._browser.get(url=url)
        log.info(str(dict(
            url=url,
            result=result,
        )))
        self.screenshot()

        end = datetime.datetime.now().timestamp()
        seconds_elapsed = int(end - start)

        log.info(str(dict(
            seconds_elapsed=seconds_elapsed,
            result=result,
        )))
        self._rate_counter.append(seconds_elapsed)

        return result

    def get_about(self, rate_limiting: bool = True):
        """get about page"""
        url = f'{self.url}/about'

        if rate_limiting:
            result = self.get_with_rate_limiter(url=url)
        else:
            result = self.get(url=url)

        log.info(str(dict(
            url=url,
            result=result,
        )))
        self.screenshot()
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
            self._wait_between_retries = wait_between_retries

        result = None
        while retry < retries:

            if self.rate_limited():
                self.rate_limit_increase()

                self._rate_counter.append(self._wait_between_retries)
                Sleeper.seconds(seconds=self._wait_between_retries)
                log.error(str(dict(
                    url=url,
                    retry=retry,
                    retries=retries,
                )))
                continue
            else:
                self.rate_limit_decrease()

            result = self.get(url=url)
            self.screenshot()
            log.info(f'{result}')
            return result

            retry = retry + 1

        log.error(f'{url}')
        self.screenshot_error()
        return result

    def rate_limit_decrease(self, multiplier: int = 0.75):
        before = self._wait_between_retries
        self._wait_between_retries = abs(int(self._wait_between_retries * multiplier))

        if self._wait_between_retries == 0:
            self._wait_between_retries = 1

        log.info(str(dict(
            before=before,
            after=self._wait_between_retries,
            multiplier=multiplier,
        )))
        return self._wait_between_retries

    def rate_limit_increase(self, multiplier: int = 2):
        before = self._wait_between_retries
        self._wait_between_retries = abs(int(self._wait_between_retries * multiplier))

        log.info(str(dict(
            before=before,
            after=self._wait_between_retries,
            multiplier=multiplier,
        )))
        return self._wait_between_retries

    def rate_limited(self):
        """rate limit checker"""
        if self.current_rate_too_fast():
            log.info(True)
            self.screenshot()
            return True

        if self.temporarily_blocked() or self.must_login():
            log.info(True)
            self.screenshot()
            return True

        log.error(False)
        self.screenshot_error()
        return False

    def run(self):
        """run selenium browser"""
        if self._browser:
            log.info(f'{self._browser}')
            return self._browser.run()

    def reset_rate_counter(self):
        self._rate_counter = []
        log.info(self._rate_counter)
        return self._rate_counter

    def restart(self):
        """quit and start new instance of selenium"""
        if self._browser:
            self.quit()
        log.info(f'{self._browser}')
        return self.start()

    def screenshot(self, filename: str = 'screenshot.png'):
        screenshot = self._browser.save_screenshot(filename=filename, folder='.')
        log.info(f'{screenshot}')
        return screenshot

    def screenshot_error(self):
        """get error screenshot"""
        screenshot = self.screenshot(filename='screenshot-error.png')
        log.debug(f'{screenshot}')
        return screenshot

    def screenshot_success(self):
        """get success screenshot"""
        screenshot = self.screenshot(filename='screenshot-success.png')
        log.debug(f'{screenshot}')
        return screenshot

    def set_url(self, url: str) -> str:
        """set new url"""
        self._url = url
        return self.url

    def start(self, headless: bool = True, random_user_agent: bool = False, set_user_agent: str = None):
        """start new instance of selenium"""
        self._browser.config.webdriver_wrapper = ChromeWrapper()

        if headless:
            self._browser.config.webdriver_wrapper.enable_headless().set_locale_experimental()
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

        log.info(str(dict(
            browser=self._browser
        )))
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
            log.info(f'{self._browser}')
            return self._browser.quit()
