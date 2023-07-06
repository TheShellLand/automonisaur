import os
import warnings
import selenium
import selenium.webdriver

from automon.log import Logging
from automon.helpers.osWrapper.environ import environ

from .config_window_size import set_window_size

log = Logging(name='ConfigChrome', level=Logging.INFO)


class ConfigChrome(object):

    def __init__(self):
        self._webdriver = None
        self._chrome_options = selenium.webdriver.ChromeOptions()
        self._chromedriver = environ('SELENIUM_CHROMEDRIVER_PATH')

        self._path_updated = None
        self.update_paths()

        self._window_size = set_window_size()

    def __repr__(self):
        if self.chromedriver:
            return f'Chrome {self.chromedriver}'
        return f'Chrome'

    @property
    def chrome_options(self):
        return self._chrome_options

    @property
    def chrome_options_arg(self):
        return self.chrome_options.arguments

    @property
    def chromedriver(self):
        return self._chromedriver

    @property
    def webdriver(self) -> selenium.webdriver.Chrome:
        return self._webdriver

    @property
    def window_size(self):
        return self._window_size

    def disable_certificate_verification(self):
        warnings.warn('Certificates are not verified', Warning)
        self.chrome_options.add_argument('--ignore-certificate-errors')
        return self

    def disable_extensions(self):
        self.chrome_options.add_argument("--disable-extensions")

    def disable_infobars(self):
        self.chrome_options.add_argument("--disable-infobars")
        return self

    def disable_notifications(self):
        """Pass the argument 1 to allow and 2 to block

        """
        self.chrome_options.add_experimental_option(
            "prefs", {"profile.default_content_setting_values.notifications": 2}
        )
        return self

    def disable_sandbox(self):
        self.chrome_options.add_argument('--no-sandbox')
        return self

    def disable_shm(self):
        warnings.warn('Disabled shm will use disk I/O, and will be slow', Warning)
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        return self

    def enable_bigshm(self):
        warnings.warn('Big shm not yet implemented', Warning)
        return self

    def enable_defaults(self):
        self.enable_maximized()
        return self

    def enable_fullscreen(self):
        self.chrome_options.add_argument("--start-fullscreen")
        return self

    def enable_headless(self):
        self.chrome_options.add_argument('headless')
        return self

    def enable_notifications(self):
        """Pass the argument 1 to allow and 2 to block

        """
        self.chrome_options.add_experimental_option(
            "prefs", {"profile.default_content_setting_values.notifications": 1}
        )
        return self

    def enable_maximized(self):
        self.chrome_options.add_argument('--start-maximized')
        return self

    def close(self):
        """close

        """
        return self.webdriver.close()

    def in_docker(self):
        """Chrome best used with docker

        """
        self.enable_defaults()
        self.enable_headless()
        self.disable_sandbox()
        self.disable_infobars()
        self.disable_extensions()
        self.disable_notifications()
        return self

    def in_headless(self):
        """alias to headless sandboxed

        """
        return self.in_headless_sandboxed()

    def in_headless_sandboxed(self):
        """Headless Chrome with sandbox enabled

        """
        warnings.warn('Docker does not support sandbox option')
        warnings.warn('Default shm size is 64m, which will cause chrome driver to crash.', Warning)

        self.enable_defaults()
        self.enable_headless()
        return self

    def in_headless_sandbox_disabled(self):
        """Headless Chrome with sandbox disabled

        """
        warnings.warn('Default shm size is 64m, which will cause chrome driver to crash.', Warning)

        self.enable_defaults()
        self.enable_headless()
        self.disable_sandbox()
        return self

    def in_headless_sandbox_disabled_certificate_unverified(self):
        """Headless Chrome with sandbox disabled with no certificate verification

        """
        warnings.warn('Default shm size is 64m, which will cause chrome driver to crash.', Warning)

        self.enable_defaults()
        self.enable_headless()
        self.disable_sandbox()
        self.disable_certificate_verification()
        return self

    def in_headless_sandbox_disabled_shm_disabled(self):
        """Headless Chrome with sandbox disabled

        """
        self.enable_defaults()
        self.enable_headless()
        self.disable_sandbox()
        self.disable_shm()
        return self

    def in_headless_sandbox_disabled_bigshm(self):
        """Headless Chrome with sandbox disabled

        """
        warnings.warn('Larger shm option is not implemented', Warning)

        self.enable_defaults()
        self.enable_headless()
        self.enable_bigshm()
        self.disable_sandbox()
        return self

    def in_remote_driver(self, host: str = '127.0.0.1', port: str = '4444', executor_path: str = '/wd/hub'):
        """Remote Selenium

        """
        log.info(
            f'Remote WebDriver Hub URL: http://{host}:{port}{executor_path}/static/resource/hub.html')

        selenium.webdriver.Remote(
            command_executor=f'http://{host}:{port}{executor_path}',
            desired_capabilities=selenium.webdriver.common.desired_capabilities.DesiredCapabilities.CHROME
        )

    def in_sandbox(self):
        """Chrome with sandbox enabled

        """
        warnings.warn('Docker does not support sandbox option')
        warnings.warn('Default shm size is 64m, which will cause chrome driver to crash.', Warning)

        self.enable_defaults()
        return self

    def in_sandbox_disabled(self):
        """Chrome with sandbox disabled

        """
        warnings.warn('Default shm size is 64m, which will cause chrome driver to crash.', Warning)

        self.enable_defaults()
        self.disable_sandbox()
        return self

    def run(self):
        log.info(f'starting {self}')
        try:
            if self.chromedriver:
                self._webdriver = selenium.webdriver.Chrome(executable_path=self.chromedriver,
                                                            options=self.chrome_options)
                return self.webdriver

            self._webdriver = selenium.webdriver.Chrome(options=self.chrome_options)
            return self.webdriver
        except Exception as e:
            log.error(f'Browser not set. {e}', enable_traceback=False)

    def set_chromedriver(self, chromedriver: str):
        self._chromedriver = chromedriver
        self.update_paths()
        return self

    def set_user_agent(self, user_agent: str):
        self.chrome_options.add_argument(f"user-agent={user_agent}")
        return self

    def set_window_size(self, *args, **kwargs):
        self._window_size = set_window_size(*args, **kwargs)
        width, height = self.window_size
        self.webdriver.set_window_size(width=width, height=height)
        return self

    def start(self):
        """alias to run

        """
        return self.run()

    def stop_client(self):
        """stop client

        """
        return self.webdriver.stop_client()

    def update_paths(self):
        if self.chromedriver:
            if not self._path_updated:
                os.environ['PATH'] = f"{os.getenv('PATH')}:{self._chromedriver}"

    def quit(self):
        """quit

        """
        return self.webdriver.quit()

    def quit_gracefully(self):
        """gracefully quit webdriver

        """
        try:
            self.close()
            self.quit()
            self.stop_client()
        except Exception as error:
            log.error(f'failed to gracefully quit. {error}')
            return False
        return True
