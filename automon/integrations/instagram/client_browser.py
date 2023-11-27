import functools

from automon.log import logger
from automon.integrations.seleniumWrapper.browser import SeleniumBrowser
from automon.integrations.seleniumWrapper.config_webdriver_chrome import ChromeWrapper

from automon.helpers.sleeper import Sleeper
# from automon.integrations.minioWrapper import MinioClient

from .config import InstagramConfig
from .urls import Urls
from .xpaths import XPaths

log = logger.logging.getLogger(__name__)
log.setLevel(logger.DEBUG)


class InstagramBrowserClient:
    login: str
    password: str
    config: InstagramConfig
    browser: SeleniumBrowser

    def __init__(self,
                 login: str = None,
                 password: str = None,
                 config: InstagramConfig = None,
                 headless: bool = True):
        """Instagram Browser Client"""
        self.config = config or InstagramConfig(login=login, password=password)
        self.browser = SeleniumBrowser()
        self.browser.config.webdriver_wrapper = ChromeWrapper()

        self.useragent = self.browser.get_random_user_agent()

        if headless:
            self.browser.config.webdriver_wrapper.in_headless().set_user_agent(self.useragent)
        else:
            self.browser.config.webdriver_wrapper.set_user_agent(self.useragent)

    def __repr__(self):
        return f'{self.__dict__}'

    def _is_running(func):
        @functools.wraps(func)
        def wrapped(self, *args, **kwargs):
            if self.is_running():
                return func(self, *args, **kwargs)
            return False

        return wrapped

    def _is_authenticated(func):
        @functools.wraps(func)
        def wrapped(self, *args, **kwargs):
            if self.is_authenticated():
                return func(self, *args, **kwargs)
            return False

        return wrapped

    def get_page(self, account: str):
        """ Get page
        """
        log.debug(f'[get_page] getting {account}')

        page = f'https://instagram.com/{account}'
        browser = self.authenticated_browser
        return browser.get(page)

    def get_stories(self, account: str):
        """ Retrieve story
        """
        story = f'https://www.instagram.com/stories/{account}/'
        num_of_stories = 0

        log.debug(f'[get_stories] {story}')

        browser = self.authenticated_browser
        browser.get(story)
        browser.browser.save_screenshot_to_minio(bucket_name='screenshots',
                                                 prefix='instagram/' + account)

        if 'Page Not Found' in browser.browser.title:
            log.debug(f'[get_stories] no stories for {account}')
            return num_of_stories

        Sleeper.seconds(2)

        while True:
            try:
                self._next_story(browser)

                title = browser.browser.title
                if title == 'Instagram':
                    log.debug(
                        ('[get_stories] {} end of stories'.format(account)))
                    raise Exception
                num_of_stories += 1
                browser.save_screenshot_to_minio(bucket_name='screenshots',
                                                 prefix='instagram/' + account)
                Sleeper.seconds(1)
                browser.save_screenshot_to_minio(bucket_name='screenshots',
                                                 prefix='instagram/' + account)
            except Exception as error:
                # TODO: disable browser proxy when done
                log.debug(f'[get_stories] done: {account}, {error}')
                return num_of_stories

    def _next_story(self, authenticated_browser):
        """ Click next story button
        """

        xpaths = [
            '//*[@id="react-root"]/section/div/div/section/div[2]/div[1]/div/div/div[2]/div/div/button',
            '//*[@id="react-root"]/section/div/div/section/div[2]/button[2]'
        ]

        found_btn = False
        for xpath in xpaths:
            try:
                browser = authenticated_browser
                button = browser.browser.find_element_by_xpath(xpath)
                found_btn = True
                log.debug('[next_story] next story')
                return button.click()
            except Exception as error:
                log.error(f'{error}')

        if not found_btn:
            # no more stories. exit
            log.debug('[_next_story] no more stories')
            raise Exception

    def remove_not_now(self):
        """check for "save your login info" dialogue"""
        not_now = self.browser.wait_for_xpath(
            self.xpaths.save_info_not_now_div,
            fail_on_error=False
        )
        if not_now:
            self.browser.action_type(self.browser.keys.TAB)
            self.browser.action_type(self.browser.keys.TAB)
            self.browser.action_type(self.browser.keys.ENTER)
            # self.browser.action_click(not_now, 'dont save login info')

    def remove_notifications_not_now(self):
        """check for "notifications" dialogue"""
        notifications_not_now = self.browser.wait_for_xpath(
            self.xpaths.turn_on_notifications_not_now,
            fail_on_error=False
        )
        if notifications_not_now:
            self.browser.action_click(notifications_not_now, 'no notifications')

    def run_stories(self, limit=None):
        """Run
        """

        log.debug('[login] {}'.format(self.login))

        self.authenticated_browser = self.authenticate()

        # if self.authenticated_browser:
        #
        #     count = 0
        #     if limit:
        #
        #         for account in self.following:
        #             hevlog.logging.debug(
        #                 '[runrun] [{}] {} session: {}'.format(self.authenticated_browser.browser.name,
        #                                                       self.authenticated_browser.browser.title,
        #                                                       self.authenticated_browser.browser.session_id))
        #
        #             num_of_stories = get_stories(self.authenticated_browser, account)
        #
        #             hevlog.logging.info('[{}] {} stories'.format(account, num_of_stories))
        #
        #             count = count + 1
        #             if count == limit:
        #                 return
        #
        #     Sleeper.hour('instagram')
        #     self.run_stories()

    @_is_running
    def authenticate(self):
        """Authenticate to Instagram
        """

        self.browser.get(self.urls.login_page)

        # user
        login_user = self.browser.wait_for_xpath(self.xpaths.login_user)
        self.browser.action_click(login_user, 'user')
        self.browser.action_type(self.login)

        # password
        login_pass = self.browser.wait_for_xpath(self.xpaths.login_pass)
        self.browser.action_click(login_pass, 'login')
        self.browser.action_type(self.config.password)
        self.browser.action_type(self.browser.keys.ENTER)

        self.remove_notifications_not_now()
        self.remove_not_now()

        if self.is_authenticated():
            log.info(f'{True}')
            return True

        log.error(f'{False}')
        return False

    @_is_running
    @_is_authenticated
    def get_followers(self, account: str):
        url = self.urls.followers(account)
        self.browser.get(url)

    @_is_running
    def is_authenticated(self):
        try:
            if self.urls.domain not in self.browser.url:
                self.browser.get(self.urls.domain)
            self.remove_notifications_not_now()
            self.remove_not_now()
            profile_picture = self.browser.wait_for_xpath(self.xpaths.profile_picture)
            if profile_picture:
                log.info(f'{True}')
                return True
        except Exception as error:
            log.error(f'{error}')
        return False

    def is_running(self) -> bool:
        if self.config.is_configured:
            if self.browser.is_running():
                log.info(f'{True}')
                return True
        log.error(f'{False}')
        return False

    @property
    def login(self) -> str:
        return self.config.login

    @property
    def urls(self):
        return Urls()

    @property
    def xpaths(self):
        return XPaths()
