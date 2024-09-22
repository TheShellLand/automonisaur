import functools

from automon import log
from automon.integrations.seleniumWrapper import SeleniumBrowser, ChromeWrapper

from automon.helpers.sleeper import Sleeper
# from automon.integrations.minioWrapper import MinioClient

from .config import InstagramConfig
from .urls import Urls
from .xpaths import XPaths

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


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
        self.browser = None

        self.authenticated_browser = None
        self.useragent = None
        self.headless = headless

    def __repr__(self):
        return f'{self.__dict__}'

    def _is_running(func):
        @functools.wraps(func)
        def wrapped(self, *args, **kwargs):
            if self.is_ready():
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
        logger.debug(f'[get_page] getting {account}')

        page = f'https://instagram.com/{account}'
        browser = self.authenticated_browser
        return browser.get(page)

    def get_stories(self, account: str):
        """ Retrieve story
        """
        story = f'https://www.instagram.com/stories/{account}/'
        num_of_stories = 0

        logger.debug(f'[get_stories] {story}')

        browser = self.authenticated_browser
        browser.get(story)
        browser.browser.save_screenshot_to_minio(bucket_name='screenshots',
                                                 prefix='instagram/' + account)

        if 'Page Not Found' in browser.browser.title:
            logger.debug(f'[get_stories] no stories for {account}')
            return num_of_stories

        Sleeper.seconds(2)

        while True:
            try:
                self._next_story(browser)

                title = browser.browser.title
                if title == 'Instagram':
                    logger.debug(
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
                logger.debug(f'[get_stories] done: {account}, {error}')
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
                logger.debug('[next_story] next story')
                return button.click()
            except Exception as error:
                logger.error(f'{error}')

        if not found_btn:
            # no more stories. exit
            logger.debug('[_next_story] no more stories')
            raise Exception

    def remove_save_login(self):
        """check for "save your login info" dialogue"""
        try:
            self.browser.wait_for_anything(
                by=self.browser.by.TAG_NAME,
                value='Save your login info?',
                timeout=60,
                contains=False,
                return_first=True,
            )
            remove_save_login = self.browser.wait_for_anything(
                by=self.browser.by.TAG_NAME,
                value='Not now',
                contains=False,
                timeout=60,
            )
            remove_save_login = [x for x in remove_save_login
                                 if x.aria_role == 'button'
                                 if x.text == 'Not now']

            if remove_save_login:
                self.browser.save_screenshot(folder='.')
                self.browser.action_click(remove_save_login[0])

        except:
            return False

    def remove_notifications(self):
        """check for "notifications" dialogue"""
        try:
            remove_notifications = self.browser.wait_for_elements(
                by=self.browser.by.TAG_NAME,
                value='span',
                timeout=60)

            remove_notifications = [
                x for x in remove_notifications
                if x.text == 'Turn on Notifications']

            if not remove_notifications:
                return False

            remove_notifications = self.browser.wait_for_elements(
                by=self.browser.by.TAG_NAME,
                value='button',
                timeout=60)

            remove_notifications = [
                x for x in remove_notifications
                if x.text == 'Not Now']

            if remove_notifications:
                self.browser.action_click(remove_notifications[0])

        except Exception as error:
            return False

    def run_stories(self, limit=None):
        """Run
        """

        logger.debug('[login] {}'.format(self.login))

        self.authenticated_browser = self.authenticate()

        # if self.authenticated_browser:
        #
        #     count = 0
        #     if limit:
        #
        #         for account in self.following:
        #             hevlogger.debug(
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

    def authenticate(self):
        """Authenticate to Instagram
        """

        self.browser.get(self.urls.login_page)

        # user
        login_user = self.browser.wait_for_elements(
            by=self.browser.by.TAG_NAME, value='input', timeout=60)
        login_user = [x for x in login_user if x.accessible_name == 'Phone number, username, or email'][0]
        self.browser.action_click(login_user)
        self.browser.action_type(self.login, secret=True)

        # password
        login_pass = self.browser.find_elements(by=self.browser.by.TAG_NAME, value='input')
        login_pass = [x for x in login_pass if x.accessible_name == 'Password'][0]
        self.browser.action_click(login_pass)
        self.browser.action_type(self.config.password, secret=True)
        self.browser.action_type(self.browser.keys.ENTER)

        self.remove_notifications()
        self.remove_save_login()

        if self.is_authenticated():
            logger.info(f'logged in')
            return True

        logger.error(f'login failed')
        return False

    def get_followers(self, account: str):
        url = self.urls.followers(account)
        self.browser.get(url)

    def is_authenticated(self):
        try:
            self.remove_notifications()
            self.browser.get(self.urls.domain)

            is_authenticated = self.browser.wait_for_elements(
                by=self.browser.by.TAG_NAME,
                value='img')

            is_authenticated = [
                x for x in is_authenticated
                if x.accessible_name == f"{self.config.login}'s profile picture"
            ]

            if is_authenticated:
                logger.info(f'authenticated')
                return True
        except Exception as error:
            logger.error(error)

        return False

    def is_ready(self) -> bool:
        try:
            if self.config.is_ready():
                if self.browser.is_running():
                    return True
        except Exception as error:
            logger.error(error)
        return False

    @property
    def login(self) -> str:
        return self.config.login

    def start(self):
        try:
            self.browser = SeleniumBrowser()
            self.browser.config.webdriver_wrapper = ChromeWrapper()

            self.useragent = self.browser.get_random_user_agent()

            if self.headless:
                self.browser.config.webdriver_wrapper.in_headless().set_user_agent(self.useragent)
            else:
                self.browser.config.webdriver_wrapper.set_user_agent(self.useragent)

            self.browser.start()

        except Exception as error:
            logger.error(error)

    @property
    def urls(self):
        return Urls()

    @property
    def xpaths(self):
        return XPaths()
