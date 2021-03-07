from selenium.webdriver.common.keys import Keys

from automon import Logging
from automon.integrations.selenium import (SeleniumBrowser, chrome_for_docker)

from automon.helpers.sleeper import Sleeper
from automon.integrations.minio import MinioClient

hevlog = Logging('instagram', level=Logging.INFO)


class Instagram:

    def __init__(self, instagram_login, instagram_password, instagram_following,
                 minio_hosts, minio_access_key, minio_secret_key,
                 browser=Browser(chrome_for_docker())):
        """Class for controlling Instagram without API
        """

        self.login = instagram_login
        self.password = instagram_password
        self.following = instagram_following

        self.browser = browser
        # self.authenticated_browser = None

        self.minio_client = MinioClient(hosts=minio_hosts,
                                        access_key=minio_access_key,
                                        secret_key=minio_secret_key,
                                        secure=False)

    def run_stories(self, limit=None):
        """Run
        """

        hevlog.logging.debug('[login] {}'.format(self.login))
        hevlog.logging.info('Running...')
        hevlog.logging.info('[accounts] {}'.format(len(self.following)))

        self.authenticated_browser = self._authenticate()

        if self.authenticated_browser and self.following:

            count = 0
            if limit:

                for account in self.following:
                    hevlog.logging.debug(
                        '[runrun] [{}] {} session: {}'.format(self.authenticated_browser.browser.name,
                                                              self.authenticated_browser.browser.title,
                                                              self.authenticated_browser.browser.session_id))

                    num_of_stories = get_stories(self.authenticated_browser, account)

                    hevlog.logging.info('[{}] {} stories'.format(account, num_of_stories))

                    count = count + 1
                    if count == limit:
                        return

            Sleeper.hour('instagram')
            self.run_stories()

    def _authenticate(self):
        """Authenticate to Instagram
        """

        browser = self.browser

        # TODO: create capture proxy
        #       send traffic to /api
        login_page = 'https://www.instagram.com/accounts/login/?source=auth_switcher'

        browser.new_resolution('1024x768')

        if self.minio_client.connected:
            browser.set_minio_client(self.minio_client)

        browser.browser.get(login_page)

        hevlog.logging.debug('[authenticate] {}'.format(login_page))

        Sleeper.seconds('instagram get page', 1)

        browser.type(Keys.TAB)
        browser.type(self.login)

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
            pass
        else:
            hevlog.logging.error('[browser] Authentication failed')

            hevlog.logging.debug(
                '[browser] Found password field: {} Found login button: {}'.format(browser.browser.name,
                                                                                   found_pass,
                                                                                   found_btn))

            Sleeper.minute("instagram can't authenticate")
            return False

        login_pass.send_keys(self.password)
        login_btn.click()

        Sleeper.seconds('wait for instagram to log in', 5)

        hevlog.logging.debug(
            '[authenticated browser] [{}] {} session: {}'.format(browser.browser.name, browser.browser.title,
                                                                 browser.browser.session_id))

        browser.save_screenshot_to_minio(bucket_name='screenshots', prefix='instagram/')

        return browser

    def _get_stories(self, account):
        """ Retrieve story
        """
        story = 'https://www.instagram.com/stories/{}/'.format(account)
        num_of_stories = 0

        hevlog.logging.debug('[get_stories] {}'.format(story))

        browser = self.authenticated_browser
        browser.browser.get(story)
        browser.browser.save_screenshot_to_minio(bucket_name='screenshots', prefix='instagram/' + account)

        if 'Page Not Found' in browser.browser.title:
            hevlog.logging.debug('[get_stories] no stories for {}'.format(account))
            return num_of_stories

        Sleeper.seconds('instagram', 2)

        while True:
            try:
                next_story(browser)

                title = browser.browser.title
                if title == 'Instagram':
                    hevlog.logging.debug(('[get_stories] {} end of stories'.format(account)))
                    raise Exception
                num_of_stories += 1
                browser.save_screenshot_to_minio(bucket_name='screenshots', prefix='instagram/' + account)
                Sleeper.seconds('watch the story for a bit', 1)
                browser.save_screenshot_to_minio(bucket_name='screenshots', prefix='instagram/' + account)
            except:
                # TODO: disable browser proxy when done
                hevlog.logging.debug('[get_stories] done: {}'.format(account))
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
                hevlog.logging.debug('[next_story] next story')
                return button.click()
            except:
                pass

        if not found_btn:
            # no more stories. exit
            hevlog.logging.debug('[_next_story] no more stories')
            raise Exception

    def _get_page(self, account):
        """ Get page
        """
        hevlog.logging.debug('[_get_page] getting {}'.format(account))

        page = 'https://instagram.com/{}'.format(account)
        browser = self.authenticated_browser
        return browser.browser.get(page)


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

        # browser = Browser(chrome())
        # browser = Browser(chrome_headless_nosandbox())
        browser = Browser(chrome_for_docker())
        # browser = Browser(chrome_sandboxed())
        # browser = Browser(chrome_headless_sandboxed())
        # browser = Browser(chrome_remote())

        browser.new_resolution('1024x768')

        if minio_client:
            browser.set_minio_client(minio_client)

        browser.browser.get(login_page)

        hevlog.logging.debug('[authenticate] {}'.format(login_page))

        Sleeper.seconds('instagram get page', 1)

        browser.type(Keys.TAB)
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
            hevlog.logging.error('[browser] Authentication failed')

            hevlog.logging.debug(
                '[browser] Found password field: {} Found login button: {}'.format(browser.browser.name, found_pass,
                                                                                   found_btn))

            Sleeper.minute("instagram can't authenticate")

    login_pass.send_keys(password)
    login_btn.click()

    Sleeper.seconds('wait for instagram to log in', 5)

    hevlog.logging.debug(
        '[authenticated browser] [{}] {} session: {}'.format(browser.browser.name, browser.browser.title,
                                                             browser.browser.session_id))
    browser.save_screenshot_to_minio(bucket_name='screenshots', prefix='instagram/')

    return browser


def get_stories(authenticated_browser, account):
    """ Retrieve story
    """
    story = 'https://www.instagram.com/stories/{}/'.format(account)
    num_of_stories = 0
    # TODO: set browser to redirect to proxy here
    # TODO: check if account exists
    browser = authenticated_browser

    hevlog.logging.debug('[get_stories] {}'.format(story))

    browser.browser.get(story)
    browser.save_screenshot_to_minio(bucket_name='screenshots', prefix='instagram/' + account)

    if 'Page Not Found' in browser.browser.title:
        hevlog.logging.debug('[get_stories] no stories for {}'.format(account))
        return num_of_stories

    Sleeper.seconds('instagram', 2)

    while True:
        try:
            next_story(browser)

            title = browser.browser.title
            if title == 'Instagram':
                hevlog.logging.debug(('[get_stories] {} end of stories'.format(account)))
                raise Exception
            num_of_stories += 1
            browser.save_screenshot_to_minio(bucket_name='screenshots', prefix='instagram/' + account)
            Sleeper.seconds('watch the story for a bit', 1)
            browser.save_screenshot_to_minio(bucket_name='screenshots', prefix='instagram/' + account)
        except:
            # TODO: disable browser proxy when done
            hevlog.logging.debug('[get_stories] done: {}'.format(account))
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
            hevlog.logging.debug('[next_story] next story')
            return button.click()
        except:
            pass

    if not found_btn:
        # no more stories. exit
        hevlog.logging.debug('[next_story] no more stories')
        raise Exception


def get_page(authenticated_browser, account):
    """ Get page
    """
    # TODO: need to download page
    hevlog.logging.debug('[get_page] getting {}'.format(account))
    page = 'https://instagram.com/{}'.format(account)
    browser = authenticated_browser
    return browser.browser.get(page)


def runrun(browser, account):
    hevlog.logging.debug(
        '[runrun] [{}] {} session: {}'.format(browser.browser.name, browser.browser.title,
                                              browser.browser.session_id))

    num_of_stories = get_stories(browser, account)

    hevlog.logging.info('[{}] {} stories'.format(account, num_of_stories))

    # Sleeper.minute('instagram')

    return True


def test_run(config):
    client = MinioClient(config['minio-hev'], secure=False)

    instagram_config = config['instagram']
    login = instagram_config['login']['account']
    password = instagram_config['login']['password']
    accounts = instagram_config['following']

    hevlog.logging.debug('[login] {}'.format(login))
    hevlog.logging.info('Running...')
    hevlog.logging.info('[accounts] {}'.format(len(accounts)))

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
