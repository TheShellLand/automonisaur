import os
import warnings
import selenium

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from automon.log.logger import Logging

log = Logging(name='selenium', level=Logging.INFO)


class SeleniumConfig:

    def __init__(self, webdriver: selenium.webdriver = None, chromedriver: str = None):
        self.webdriver = webdriver or selenium.webdriver
        self.SELENIUM_CHROMEDRIVER_PATH = chromedriver or os.getenv('SELENIUM_CHROMEDRIVER_PATH') or ''

        if self.SELENIUM_CHROMEDRIVER_PATH:
            os.environ['PATH'] = f"{os.getenv('PATH')}:{self.SELENIUM_CHROMEDRIVER_PATH}"

    def chrome(self):
        """Chrome with no options

        """
        opt = SeleniumOptions(self.webdriver)
        opt.default()

    def chrome_maximized(self):
        """Chrome with no options

        """
        opt = SeleniumOptions(self.webdriver)
        opt.default()
        opt.maximized()

    def chrome_fullscreen(self):
        """Chrome with no options

        """
        opt = SeleniumOptions(self.webdriver)
        opt.default()
        opt.fullscreen()

    def chrome_for_docker(self):
        """Chrome best used with docker

        """
        opt = SeleniumOptions(self.webdriver)
        opt.default()
        opt.nosandbox()
        opt.headless()
        opt.noinfobars()
        opt.noextensions()
        opt.nonotifications()

    def chrome_sandboxed(self):
        """Chrome with sandbox enabled

        """
        warnings.warn('Docker does not support sandbox option')
        warnings.warn('Default shm size is 64m, which will cause chrome driver to crash.', Warning)

        opt = SeleniumOptions(self.webdriver)
        opt.default()

    def chrome_nosandbox(self):
        """Chrome with sandbox disabled

        """
        warnings.warn('Default shm size is 64m, which will cause chrome driver to crash.', Warning)

        opt = SeleniumOptions(self.webdriver)
        opt.default()
        opt.nosandbox()

    def chrome_headless_sandboxed(self):
        """Headless Chrome with sandbox enabled

        """
        warnings.warn('Docker does not support sandbox option')
        warnings.warn('Default shm size is 64m, which will cause chrome driver to crash.', Warning)

        opt = SeleniumOptions(self.webdriver)
        opt.default()
        opt.headless()

    def chrome_headless_nosandbox(self):
        """Headless Chrome with sandbox disabled

        """
        warnings.warn('Default shm size is 64m, which will cause chrome driver to crash.', Warning)

        opt = SeleniumOptions(self.webdriver)
        opt.default()
        opt.headless()
        opt.nosandbox()

    def chrome_headless_nosandbox_unsafe(self):
        """Headless Chrome with sandbox disabled with not certificate verification

        """
        warnings.warn('Default shm size is 64m, which will cause chrome driver to crash.', Warning)

        opt = SeleniumOptions(self.webdriver)
        opt.default()
        opt.headless()
        opt.nosandbox()
        opt.unsafe()

    def chrome_headless_nosandbox_noshm(self):
        """Headless Chrome with sandbox disabled

        """
        opt = SeleniumOptions(self.webdriver)
        opt.default()
        opt.headless()
        opt.nosandbox()
        opt.noshm()

    def chrome_headless_nosandbox_bigshm(self):
        """Headless Chrome with sandbox disabled

        """
        warnings.warn('Larger shm option is not implemented', Warning)

        opt = SeleniumOptions(self.webdriver)
        opt.default()
        opt.headless()
        opt.nosandbox()
        opt.bigshm()

    def chrome_remote(self, host: str = '127.0.0.1', port: str = '4444', executor_path: str = '/wd/hub'):
        """Remote Selenium

        """
        log.info(
            f'Remote WebDriver Hub URL: http://{host}:{port}{executor_path}/static/resource/hub.html')

        self.webdriver.Remote(
            command_executor=f'http://{host}:{port}{executor_path}',
            desired_capabilities=DesiredCapabilities.CHROME
        )


class SeleniumOptions:

    def __init__(self, webdriver: selenium.webdriver):
        self.webdriver = webdriver or selenium.webdriver
        self.options = self.webdriver.ChromeOptions()

    def default(self):
        self.options.add_argument('start-maximized')

    def unsafe(self):
        warnings.warn('Certificates are not verified', Warning)
        self.options.add_argument('--ignore-certificate-errors')

    def nosandbox(self):
        self.options.add_argument('--no-sandbox')

    def headless(self):
        self.options.add_argument('headless')

    def noshm(self):
        warnings.warn('Disabled shm will use disk I/O, and will be slow', Warning)
        self.options.add_argument('--disable-dev-shm-usage')

    def bigshm(self):
        warnings.warn('Big shm not yet implemented', Warning)

    def noinfobars(self):
        self.options.add_argument("--disable-infobars")

    def noextensions(self):
        self.options.add_argument("--disable-extensions")

    def maximized(self):
        self.options.add_argument("--start-maximized")

    def fullscreen(self):
        self.options.add_argument("--start-fullscreen")

    def nonotifications(self):
        # Pass the argument 1 to allow and 2 to block
        self.options.add_experimental_option(
            "prefs", {"profile.default_content_setting_values.notifications": 1}
        )


if __name__ == "__main__":
    pass
