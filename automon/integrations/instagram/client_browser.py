import selenium
import functools

from selenium.webdriver.common.action_chains import ActionChains

from automon import Logging
from automon.integrations.seleniumWrapper.browser import SeleniumBrowser

from automon.helpers.sleeper import Sleeper
from automon.integrations.minioWrapper import MinioClient

from .config import InstagramConfig
from .urls import Urls
from .xpaths import XPaths

log = Logging('InstagramClientBrowser', level=Logging.INFO)


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
        self.browser.set_browser(self.browser.type.chrome)

        if headless:
            self.browser.set_browser(self.browser.type.chrome_headless)

    def __repr__(self):
        return f'{self.__dict__}'

    def _is_running(func):
        @functools.wraps(func)
        def wrapped(self, *args, **kwargs):
            if self.browser.is_running():
                return func(self, *args, **kwargs)
            return False

        return wrapped

    def _is_authenticated(func):
        @functools.wraps(func)
        def wrapped(self, *args, **kwargs):
            if self.browser.find_xpath(self.xpaths.profile_picture):
                return func(self, *args, **kwargs)
            return False

        return wrapped

    def _get_page(self, account):
        """ Get page
        """
        log.debug('[_get_page] getting {}'.format(account))

        page = 'https://instagram.com/{}'.format(account)
        browser = self.authenticated_browser
        return browser.get(page)

    def _get_stories(self, account):
        """ Retrieve story
        """
        story = 'https://www.instagram.com/stories/{}/'.format(account)
        num_of_stories = 0

        log.debug('[get_stories] {}'.format(story))

        browser = self.authenticated_browser
        browser.get(story)
        browser.browser.save_screenshot_to_minio(bucket_name='screenshots',
                                                 prefix='instagram/' + account)

        if 'Page Not Found' in browser.browser.title:
            log.debug('[get_stories] no stories for {}'.format(account))
            return num_of_stories

        Sleeper.seconds('instagram', 2)

        while True:
            try:
                next_story(browser)

                title = browser.browser.title
                if title == 'Instagram':
                    log.debug(
                        ('[get_stories] {} end of stories'.format(account)))
                    raise Exception
                num_of_stories += 1
                browser.save_screenshot_to_minio(bucket_name='screenshots',
                                                 prefix='instagram/' + account)
                Sleeper.seconds('watch the story for a bit', 1)
                browser.save_screenshot_to_minio(bucket_name='screenshots',
                                                 prefix='instagram/' + account)
            except:
                # TODO: disable browser proxy when done
                log.debug('[get_stories] done: {}'.format(account))
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
            except:
                pass

        if not found_btn:
            # no more stories. exit
            log.debug('[_next_story] no more stories')
            raise Exception

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
        self.browser.wait_for_xpath(self.xpaths.login_user)
        self.browser.action_click(self.xpaths.login_user, 'user')
        self.browser.action_type(self.login)

        # password
        login_pass = self.browser.wait_for_xpath(self.xpaths.login_pass)
        self.browser.action_click(login_pass, 'login')
        self.browser.action_type(self.config.password, secret=True)

        # login
        login_btn = self.browser.wait_for_xpath(self.xpaths.login_btn)
        self.browser.action_click(login_btn, 'login button')

        # check for "save your login info" dialogue
        not_now = self.browser.wait_for_xpath(self.xpaths.save_info_not_now)
        self.browser.action_click(not_now, 'dont save login info')

        # check for "notifications" dialogue
        notifications_not_now = self.browser.wait_for_xpath(self.xpaths.turn_on_notifications_not_now)
        self.browser.action_click(notifications_not_now, 'no notifications')

        log.debug(
            f'[authenticated browser] [{self.browser.browser.name}] '
            f'{self.browser.browser.title} '
            f'session: {self.browser.browser.session_id}')

        if self.browser.wait_for_xpath(self.xpaths.profile_picture):
            return True

        return False

def authenticate(username, password, minio_client=None, retries=None):
    """Authenticates through browser and returns browser driver

    :param username: username string
    :param password: password string
    :param minio_client: minio client
    :param retries: not implemented
    :return: authenticated browser
    """

    while True:

        # TODO: create capture proxy
        #       send traffic to /api
        login_page = 'https://www.instagram.com/accounts/login/?source=auth_switcher'

        # browser = SeleniumBrowser(chrome())
        # browser = SeleniumBrowser(chrome_headless_nosandbox())
        browser = SeleniumBrowser(chrome_for_docker())
        # browser = SeleniumBrowser(chrome_sandboxed())
        # browser = SeleniumBrowser(chrome_headless_sandboxed())
        # browser = SeleniumBrowser(chrome_remote())

        browser.set_resolution('1024x768')

        if minio_client:
            browser.set_minio_client(minio_client)

        browser.get(login_page)

        log.debug('[authenticate] {}'.format(login_page))

        Sleeper.seconds('instagram get page', 1)

        browser.type(selenium.webdriver.common.keys.Keys.TAB)
        browser.type(username)

        Sleeper.seconds('instagram get page', 1)

        # the password field is sometimes div[3] and div[4]
        login_pass_xpaths = [
            '//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[3]/div/label/input',
            '//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[4]/div/label/input'
        ]

        login_btn_xpaths = [
            '//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[4]/button',
            '//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[6]/button'
        ]

        found_pass = False
        for xpath in login_pass_xpaths:
            try:
                login_pass = browser.browser.find_element_by_xpath(xpath)
                found_pass = True
                break
            except:
                pass

        Sleeper.seconds('instagram get page', 2)

        found_btn = False
        for xpath in login_btn_xpaths:
            try:
                login_btn = browser.browser.find_element_by_xpath(xpath)
                found_btn = True
                break
            except:
                pass

        if found_pass and found_btn:
            break
        else:
            log.error('[browser] Authentication failed')

            log.debug(
                '[browser] Found password field: {} Found login button: {}'.format(
                    browser.browser.name,
                    found_pass,
                    found_btn))

            Sleeper.minute("instagram can't authenticate")

    login_pass.send_keys(password)
    login_btn.click()

    Sleeper.seconds('wait for instagram to log in', 5)

    log.debug(
        '[authenticated browser] [{}] {} session: {}'.format(
            browser.browser.name, browser.browser.title,
            browser.browser.session_id))
    browser.save_screenshot_to_minio(bucket_name='screenshots',
                                     prefix='instagram/')

    return browser


def get_stories(authenticated_browser, account):
    """ Retrieve story
    """
    story = 'https://www.instagram.com/stories/{}/'.format(account)
    num_of_stories = 0
    # TODO: set browser to redirect to proxy here
    # TODO: check if account exists
    browser = authenticated_browser

    log.debug('[get_stories] {}'.format(story))

    browser.get(story)
    browser.save_screenshot_to_minio(bucket_name='screenshots',
                                     prefix='instagram/' + account)

    if 'Page Not Found' in browser.browser.title:
        log.debug('[get_stories] no stories for {}'.format(account))
        return num_of_stories

    Sleeper.seconds('instagram', 2)

    while True:
        try:
            next_story(browser)

            title = browser.browser.title
            if title == 'Instagram':
                log.debug(('[get_stories] {} end of stories'.format(account)))
                raise Exception
            num_of_stories += 1
            browser.save_screenshot_to_minio(bucket_name='screenshots',
                                             prefix='instagram/' + account)
            Sleeper.seconds('watch the story for a bit', 1)
            browser.save_screenshot_to_minio(bucket_name='screenshots',
                                             prefix='instagram/' + account)
        except:
            # TODO: disable browser proxy when done
            log.debug('[get_stories] done: {}'.format(account))
            return num_of_stories


def next_story(authenticated_browser):
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
        except:
            pass

    if not found_btn:
        # no more stories. exit
        log.debug('[next_story] no more stories')
        raise Exception


def get_page(authenticated_browser, account):
    """ Get page
    """
    # TODO: need to download page
    log.debug('[get_page] getting {}'.format(account))
    page = 'https://instagram.com/{}'.format(account)
    browser = authenticated_browser
    return browser.get(page)


def runrun(browser, account):
    log.debug(
        '[runrun] [{}] {} session: {}'.format(browser.browser.name,
                                              browser.browser.title,
                                              browser.browser.session_id))

    num_of_stories = get_stories(browser, account)

    log.info('[{}] {} stories'.format(account, num_of_stories))

    # Sleeper.minute('instagram')

    return True


def test_run(config):
    client = MinioClient(config['minio-hev'], secure=False)

    instagram_config = config['instagram']
    login = instagram_config['login']['account']
    password = instagram_config['login']['password']
    accounts = instagram_config['following']

    log.debug('[login] {}'.format(login))
    log.info('Running...')
    log.info('[accounts] {}'.format(len(accounts)))

    while True:

        if len(accounts) > 0:

            browser = authenticate(login, password, client)

            for account in accounts:

                while True:
                    if runrun(browser, account):
                        break
                    else:
                        browser = authenticate(login, password, client)

                    break
                break
            break
