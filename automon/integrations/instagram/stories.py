from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from automon.log import logger
from automon.helpers.sleeper import Sleeper
from automon.integrations.seleniumWrapper.config import SeleniumConfig
from automon.integrations.seleniumWrapper.browser import SeleniumBrowser

from automon.integrations.minioWrapper import MinioClient

log = logger.logging.getLogger(__name__)
log.setLevel(logger.DEBUG)


def authenticate(username, password, minio_client=None, retries=None):
    """Authenticates through browser and returns browser driver

    :param username: username string
    :param password: password string
    :param retries: not implemented
    :return: authenticated browser
    """

    while True:

        # TODO: create capture proxy
        #       send traffic to /api
        login_page = 'https://www.instagram.com/accounts/login/?source=auth_switcher'

        # browser = SeleniumBrowser(chrome())
        # browser = SeleniumBrowser(chrome_headless_nosandbox())
        browser = SeleniumBrowser(SeleniumConfig.chrome_for_docker())
        # browser = SeleniumBrowser(chrome_sandboxed())
        # browser = SeleniumBrowser(chrome_headless_sandboxed())
        # browser = SeleniumBrowser(chrome_remote())

        if minio_client:
            browser.set_minio_client(minio_client)

        browser.browser.get(login_page)

        log.logging.debug('[authenticate] {}'.format(login_page))

        Sleeper.seconds(1)

        actions = ActionChains(browser.browser)
        actions.send_keys(Keys.TAB)
        actions.send_keys(username)
        actions.perform()

        Sleeper.seconds(1)

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

        Sleeper.seconds(2)

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
            log.logging.error('[browser] Authentication failed')

            log.logging.debug(
                '[browser] Found password field: {} Found login button: {}'.format(browser.browser.name, found_pass,
                                                                                   found_btn))

            Sleeper.minute()

    login_pass.send_keys(password)
    login_btn.click()

    Sleeper.seconds(5)

    log.logging.debug(
        '[authenticated browser] [{}] {} session: {}'.format(browser.browser.name, browser.browser.title,
                                                             browser.browser.session_id))
    browser.save_screenshot_to_minio()

    return browser


def get_stories(authenticated_browser, account):
    """ Retrieve story
    """
    story = 'https://www.instagram.com/stories/{}/'.format(account)
    num_of_stories = 0
    # TODO: set browser to redirect to proxy here
    # TODO: check if account exists
    browser = authenticated_browser

    log.logging.debug('[get_stories] {}'.format(story))

    browser.browser.get(story)
    browser.save_screenshot_to_minio(prefix=account)

    if 'Page Not Found' in browser.browser.title:
        log.logging.debug('[get_stories] no stories for {}'.format(account))
        return num_of_stories

    Sleeper.seconds(2)

    while True:
        try:
            next_story(browser)

            title = browser.browser.title
            if title == 'Instagram':
                log.logging.debug(('[get_stories] {} end of stories'.format(account)))
                raise Exception
            num_of_stories += 1
            Sleeper.seconds(1)
            browser.save_screenshot_to_minio(prefix=account)
        except:
            # TODO: disable browser proxy when done
            log.logging.debug('[get_stories] done: {}'.format(account))
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
            log.logging.debug('[next_story] next story')
            return button.click()
        except:
            pass

    if not found_btn:
        # no more stories. exit
        log.logging.debug('[next_story] no more stories')
        raise Exception


def get_page(authenticated_browser, account):
    """ Get page
    """
    # TODO: need to download page
    log.logging.debug('[get_page] getting {}'.format(account))
    page = 'https://instagram.com/{}'.format(account)
    browser = authenticated_browser
    return browser.browser.get(page)


def run(config):
    client = minio.client(config['minio-hev'], secure=False)

    instagram_config = config['instagram']
    login = instagram_config['login']['account']
    password = instagram_config['login']['password']
    accounts = instagram_config['following']

    log.logging.debug('[login] {}'.format(login))
    log.logging.info('Running...')
    log.logging.info('[accounts] {}'.format(len(accounts)))

    while True:

        if len(accounts) > 0:

            browser = authenticate(login, password, client)

            for account in accounts:

                while True:
                    if runrun(browser, account):
                        break
                    else:
                        browser = authenticate(login, password, client)

        Sleeper.hour()


def runrun(browser, account):
    log.logging.debug(
        '[runrun] [{}] {} session: {}'.format(browser.browser.name, browser.browser.title,
                                              browser.browser.session_id))

    num_of_stories = get_stories(browser, account)

    log.logging.info('[{}] {} stories'.format(account, num_of_stories))

    # Sleeper.minute('instagram')

    return True


def test_run(config):
    client = minio.client(config['minio-hev'], secure=False)

    instagram_config = config['instagram']
    login = instagram_config['login']['account']
    password = instagram_config['login']['password']
    accounts = instagram_config['following']

    log.logging.debug('[login] {}'.format(login))
    log.logging.info('Running...')
    log.logging.info('[accounts] {}'.format(len(accounts)))

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
