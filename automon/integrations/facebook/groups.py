import random
import asyncio
import datetime
import statistics

from automon import log
from automon.helpers.sleeper import Sleeper
from automon.integrations.seleniumWrapper import SeleniumBrowser, ChromeWrapper

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


class FacebookGroups(object):
    _xpath_about = [
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[3]/div/div/div/div/div/div/div[1]/div/div/div/div/div[2]/a[1]/div[1]/span',
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[3]/div/div/div/div/div/div/div[1]/div/div/div/div/div[1]/div[1]/span',
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[1]/div/div/div/div/div/div[2]/div[1]',
    ]
    _xpath_popup_close = [
        '/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/i',
    ]
    _xpath_content_unavailable = [
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[1]/div[2]/div[1]/span',
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[1]/div[2]/div[1]/span',
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

    async def content_unavailable(self):
        """This content isn't available right now"""

        try:
            text = await self._browser.wait_for_list(self._xpath_content_unavailable)
            text = text.text
            logger.debug(text)
            return text
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            logger.error(str(dict(
                url=self.url,
                message=message,
                session=session,
                stacktrace=stacktrace,
            )))
            await self.screenshot_error()

    async def creation_date(self):

        try:
            text = await self._browser.wait_for_list(self._xpath_creation_date)
            text = text.text
            logger.debug(text)
            return text
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            logger.error(str(dict(
                url=self.url,
                message=message,
                session=session,
                stacktrace=stacktrace,
            )))
            await self.screenshot_error()

    async def creation_date_timestamp(self):
        if await self.creation_date():
            # TODO: convert date to datetime timestamp
            return

    async def current_rate_too_fast(self):
        if await self.average_rate() == 0 or len(self._rate_counter) < 2:
            logger.info(False)
            return False

        if await self.average_rate() < await self.rate_per_minute():
            logger.info(True)
            return True

        return False

    async def rate_per_minute(self) -> int:
        rate = int(60 / self._rate_per_minute)
        logger.info(str(dict(
            seconds=rate,
        )))
        return rate

    async def average_rate(self):
        if self._rate_counter:
            rate = int(statistics.mean(self._rate_counter))
            logger.info(str(dict(
                seconds=rate,
            )))
            return rate
        return 0

    async def history(self):

        try:
            text = await self._browser.wait_for_list(self._xpath_history)
            text = text.text
            logger.debug(text)
            return text
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            logger.error(str(dict(
                url=self.url,
                message=message,
                session=session,
                stacktrace=stacktrace,
            )))
            await self.screenshot_error()

    async def temporarily_blocked(self):
        try:
            text = await self._browser.wait_for_list(
                self._xpath_temporarily_blocked
            )
            text = text.text
            logger.debug(text)
            return text
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            logger.error(str(dict(
                url=self.url,
                message=message,
                session=session,
                stacktrace=stacktrace,
            )))
            await self.screenshot_error()

    async def members(self):

        try:
            # TODO: need to clean up string from members and remove bad chars
            text = await self._browser.wait_for_list(self._xpath_members)
            text = text.text
            logger.debug(text)
            return text
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            logger.error(str(dict(
                url=self.url,
                message=message,
                session=session,
                stacktrace=stacktrace,
            )))
            await self.screenshot_error()

    async def members_count(self):

        if await self.members():
            count = [x for x in await self.members()]
            count = [x for x in count if x in [str(x) for x in range(0, 10)]]
            if count:
                members_count = int(''.join(count)) if count else 0

                logger.debug(members_count)
                return members_count

    async def must_login(self):
        try:
            text = await self._browser.wait_for_list(self._xpath_must_login)
            text = text.text
            logger.debug(text)
            return text
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            logger.error(str(dict(
                url=self.url,
                message=message,
                session=session,
                stacktrace=stacktrace,
            )))
            await self.screenshot_error()

    async def posts_monthly(self):

        try:
            text = await self._browser.wait_for_list(self._xpath_posts_monthly)
            text = text.text
            logger.debug(text)
            return text
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            logger.error(str(dict(
                url=self.url,
                message=message,
                session=session,
                stacktrace=stacktrace,
            )))
            await self.screenshot_error()

    async def posts_monthly_count(self):

        if await self.posts_monthly():
            count = [x for x in await self.posts_monthly()]
            count = [x for x in count if x in [str(x) for x in range(0, 10)]]
            if count:
                posts_monthly_count = int(''.join(count)) if count else 0

                logger.debug(posts_monthly_count)
                return posts_monthly_count

    async def posts_today(self):

        try:
            text = await self._browser.wait_for_list(self._xpath_posts_today)
            text = text.text
            logger.debug(text)
            return text
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            logger.error(str(dict(
                url=self.url,
                message=message,
                session=session,
                stacktrace=stacktrace,
            )))
            await self.screenshot_error()

    async def posts_today_count(self):

        if await self.posts_today():
            count = [x for x in await self.posts_today()]
            count = [x for x in count if x in [str(x) for x in range(0, 10)]]
            if count:
                posts_today_count = int(''.join(count)) if count else 0

                logger.debug(posts_today_count)
                return posts_today_count

    async def privacy(self):

        try:
            text = await self._browser.wait_for_list(self._xpath_privacy)
            text = text.text
            logger.debug(text)
            return text
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            logger.error(str(dict(
                url=self.url,
                message=message,
                session=session,
                stacktrace=stacktrace,
            )))
            await self.screenshot_error()

    async def privacy_details(self):

        try:
            text = await self._browser.wait_for_list(self._xpath_privacy_details)
            text = text.text
            logger.debug(text)
            return text
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            logger.error(str(dict(
                url=self.url,
                message=message,
                session=session,
                stacktrace=stacktrace,
            )))
            await self.screenshot_error()

    async def title(self) -> str:

        try:
            text = await self._browser.wait_for_list(self._xpath_title)
            text = text.text
            logger.debug(text)
            return text
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            logger.error(str(dict(
                url=self.url,
                message=message,
                session=session,
                stacktrace=stacktrace,
            )))
            await self.screenshot_error()

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

    async def visible(self) -> str:

        try:
            text = await self._browser.wait_for_list(self._xpath_visible)
            text = text.text
            logger.debug(text)
            return text
        except Exception as error:
            message, session, stacktrace = self.error_parsing(error)
            logger.error(str(dict(
                url=self.url,
                message=message,
                session=session,
                stacktrace=stacktrace,
            )))
            await self.screenshot_error()

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

    async def get(self, url: str) -> bool:
        """get url"""

        start = datetime.datetime.now().timestamp()

        result = await self._browser.get(url=url)
        logger.info(str(dict(
            url=url,
            result=result,
        )))
        await self.screenshot()

        end = datetime.datetime.now().timestamp()
        seconds_elapsed = int(end - start)

        logger.info(str(dict(
            seconds_elapsed=seconds_elapsed,
            result=result,
        )))
        self._rate_counter.append(seconds_elapsed)

        return result

    async def get_about(self, rate_limiting: bool = True):
        """get about page"""
        url = f'{self.url}/about'

        if rate_limiting:
            result = await self.get_with_rate_limiter(url=url)
        else:
            result = await self.get(url=url)

        logger.info(str(dict(
            url=url,
            result=result,
        )))
        await self.screenshot()
        return result

    async def get_with_rate_limiter(
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

            if await self.rate_limited():
                await self.rate_limit_increase()

                self._rate_counter.append(self._wait_between_retries)
                Sleeper.seconds(seconds=self._wait_between_retries)
                logger.error(str(dict(
                    url=url,
                    retry=retry,
                    retries=retries,
                )))
                continue
            else:
                await self.rate_limit_decrease()

            result = await self.get(url=url)
            await self.screenshot()
            logger.info(f'{result}')
            return result

            retry = retry + 1

        logger.error(f'{url}')
        await self.screenshot_error()
        return result

    async def rate_limit_decrease(self, multiplier: int = 0.75):
        before = self._wait_between_retries
        self._wait_between_retries = abs(int(self._wait_between_retries * multiplier))

        if self._wait_between_retries == 0:
            self._wait_between_retries = 1

        logger.info(str(dict(
            before=before,
            after=self._wait_between_retries,
            multiplier=multiplier,
        )))
        return self._wait_between_retries

    async def rate_limit_increase(self, multiplier: int = 2):
        before = self._wait_between_retries
        self._wait_between_retries = abs(int(self._wait_between_retries * multiplier))

        logger.info(str(dict(
            before=before,
            after=self._wait_between_retries,
            multiplier=multiplier,
        )))
        return self._wait_between_retries

    async def rate_limited(self):
        """rate limit checker"""
        if await self.current_rate_too_fast():
            logger.info(True)
            await self.screenshot()
            return True

        if await self.temporarily_blocked() or await self.must_login():
            logger.info(True)
            await self.screenshot()
            return True

        logger.error(False)
        await self.screenshot_error()
        return False

    async def run(self):
        """run selenium browser"""
        if self._browser:
            logger.info(f'{self._browser}')
            return self._browser.run()

    async def reset_rate_counter(self):
        self._rate_counter = []
        logger.info(self._rate_counter)
        return self._rate_counter

    async def restart(self):
        """quit and start new instance of selenium"""
        if self._browser:
            await self.quit()
        logger.info(f'{self._browser}')
        return self.start()

    async def screenshot(self, filename: str = 'screenshot.png'):
        try:
            screenshot = await self._browser.save_screenshot(filename=filename, folder='.')
            logger.debug(f'{screenshot}')
            return screenshot
        except Exception as error:
            raise Exception(error)

    async def screenshot_error(self):
        """get error screenshot"""
        screenshot = await self.screenshot(filename='screenshot-error.png')
        logger.debug(f'{screenshot}')
        return screenshot

    async def screenshot_success(self):
        """get success screenshot"""
        screenshot = await self.screenshot(filename='screenshot-success.png')
        logger.debug(f'{screenshot}')
        return screenshot

    async def set_url(self, url: str) -> str:
        """set new url"""
        self._url = url
        return self.url

    async def start(self, headless: bool = True, random_user_agent: bool = False, set_user_agent: str = None):
        """start new instance of selenium"""
        self._browser.config.webdriver_wrapper = ChromeWrapper()

        if headless:
            self._browser.config.webdriver_wrapper.enable_headless()
            self._browser.config.webdriver_wrapper.set_locale_experimental()
        else:
            self._browser.config.webdriver_wrapper.set_locale_experimental()

        if random_user_agent:
            self._browser.config.webdriver_wrapper.set_user_agent(
                await self._browser.get_random_user_agent()
            )
        elif set_user_agent:
            self._browser.config.webdriver_wrapper.set_user_agent(
                set_user_agent
            )

        logger.info(str(dict(
            browser=self._browser
        )))
        browser = await self._browser.run()
        self._browser.config.webdriver_wrapper.set_window_size(width=1920 * 0.6, height=1080)
        return browser

    async def stop(self):
        """alias to quit"""
        return await self.quit()

    async def to_dict(self):
        return dict(
            content_unavailable=await self.content_unavailable(),
            creation_date=await self.creation_date(),
            creation_date_timestamp=await self.creation_date_timestamp(),
            history=await self.history(),
            members=await self.members(),
            members_count=await self.members_count(),
            posts_monthly=await self.posts_monthly(),
            posts_monthly_count=await self.posts_monthly_count(),
            posts_today=await self.posts_today(),
            posts_today_count=await self.posts_today_count(),
            privacy=await self.privacy(),
            privacy_details=await self.privacy_details(),
            title=await self.title(),
            url=self.url,
            visible=await self.visible(),
        )

    async def quit(self):
        """quit selenium"""
        if self._browser:
            logger.info(f'{self._browser}')
            return await self._browser.quit()
