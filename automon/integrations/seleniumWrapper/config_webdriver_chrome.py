import os
import warnings
import selenium
import selenium.webdriver

from automon.log import logger
from automon.helpers.osWrapper.environ import environ

from .config_window_size import set_window_size

log = logger.logging.getLogger(__name__)
log.setLevel(logger.DEBUG)


class ChromeWrapper(object):

    def __init__(self):
        self._webdriver = None
        self._chrome_options = selenium.webdriver.ChromeOptions()
        self._chromedriver_path = environ('SELENIUM_CHROMEDRIVER_PATH')
        self._ChromeService = None

        self.update_paths()

        self._window_size = set_window_size()

    def __repr__(self):
        if self._webdriver:
            return str(dict(
                name=self.webdriver.name,
                window_size=self.window_size,
                browserVersion=self.browserVersion,
                chromedriverVersion=self.chromedriverVersion,
                chromedriver_path=self.chromedriver_path,
                webdriver=self.webdriver,
            ))

        return f'{__class__}'

    @property
    def browserVersion(self):
        if self.webdriver:
            return self.webdriver.capabilities.get('browserVersion')

    @property
    def chrome_options(self):
        return self._chrome_options

    @property
    def chrome_options_arg(self):
        return self.chrome_options.arguments

    @property
    def chromedriver_path(self):
        return self._chromedriver_path

    @property
    def chromedriverVersion(self):
        if self.webdriver:
            return self.webdriver.capabilities.get('chrome').get('chromedriverVersion')

    @property
    def ChromeService(self):
        return self._ChromeService

    @property
    def webdriver(self) -> selenium.webdriver.Chrome:
        return self._webdriver

    @property
    def window_size(self):
        return self._window_size

    def disable_certificate_verification(self):
        log.warning('Certificates are not verified')
        self.chrome_options.add_argument('--ignore-certificate-errors')
        log.debug(str(dict(
            add_argument='--ignore-certificate-errors'
        )))
        return self

    def disable_extensions(self):
        self.chrome_options.add_argument("--disable-extensions")
        log.debug(str(dict(
            add_argument=f'--disable-extensions'
        )))
        return self

    def disable_infobars(self):
        self.chrome_options.add_argument("--disable-infobars")
        log.debug(str(dict(
            add_argument=f'--disable-infobars'
        )))
        return self

    def disable_notifications(self):
        """Pass the argument 1 to allow and 2 to block

        """
        self.chrome_options.add_experimental_option(
            "prefs", {"profile.default_content_setting_values.notifications": 2}
        )

        log.debug(str(dict(
            add_experimental_option=("prefs", {"profile.default_content_setting_values.notifications": 2})
        )))
        return self

    def disable_sandbox(self):
        self.chrome_options.add_argument('--no-sandbox')
        log.debug(str(dict(
            add_argument=f'--no-sandbox'
        )))
        return self

    def disable_shm(self):
        log.warning('Disabled shm will use disk I/O, and will be slow')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        log.debug(str(dict(
            add_argument=f'--disable-dev-shm-usage'
        )))
        return self

    def enable_bigshm(self):
        log.warning('Big shm not yet implemented')
        return self

    def enable_defaults(self):
        self.enable_maximized()
        return self

    def enable_fullscreen(self):
        self.chrome_options.add_argument("--start-fullscreen")
        log.debug(str(dict(
            add_argument=f'--start-fullscreen'
        )))
        return self

    def enable_headless(self):
        self.chrome_options.add_argument('headless')
        log.debug(str(dict(
            add_argument='headless'
        )))
        return self

    def enable_notifications(self):
        """Pass the argument 1 to allow and 2 to block

        """
        self.chrome_options.add_experimental_option(
            "prefs", {"profile.default_content_setting_values.notifications": 1}
        )
        log.debug(str(dict(
            add_experimental_option=("prefs", {"profile.default_content_setting_values.notifications": 1})
        )))
        return self

    def enable_maximized(self):
        self.chrome_options.add_argument('--start-maximized')
        log.debug(str(dict(
            add_argument='--start-maximized'
        )))
        return self

    def enable_translate(self, native_language: str = 'en'):
        prefs = {
            "translate_whitelists": {"your native language": native_language},
            "translate": {"enabled": "True"}
        }
        self.chrome_options.add_experimental_option(
            name="prefs",
            value=prefs,
        )

        log.debug(str(dict(
            add_experimental_option=dict(
                name="prefs",
                value=prefs,
            )
        )))
        return self

    def close(self):
        """close

        """
        result = self.webdriver.close()
        log.info(f'{result}')
        return result

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
        log.warning(
            'Docker does not support sandbox option. '
            'Default shm size is 64m, which will cause chrome driver to crash.'
        )

        self.enable_defaults()
        self.enable_headless()
        return self

    def in_headless_sandbox_disabled(self):
        """Headless Chrome with sandbox disabled

        """
        log.warning('Default shm size is 64m, which will cause chrome driver to crash.')

        self.enable_defaults()
        self.enable_headless()
        self.disable_sandbox()
        return self

    def in_headless_sandbox_disabled_certificate_unverified(self):
        """Headless Chrome with sandbox disabled with no certificate verification

        """
        log.warning('Default shm size is 64m, which will cause chrome driver to crash.')

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
        log.warning('Larger shm option is not implemented')

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
        return self

    def in_sandbox(self):
        """Chrome with sandbox enabled

        """
        log.warning(
            'Docker does not support sandbox option. '
            'Default shm size is 64m, which will cause chrome driver to crash.'
        )

        self.enable_defaults()
        return self

    def in_sandbox_disabled(self):
        """Chrome with sandbox disabled

        """
        log.warning('Default shm size is 64m, which will cause chrome driver to crash.')

        self.enable_defaults()
        self.disable_sandbox()
        return self

    def run(self) -> selenium.webdriver.Chrome:
        try:
            if self.chromedriver_path:
                self._ChromeService = selenium.webdriver.ChromeService(
                    executable_path=self.chromedriver_path
                )
                log.debug(str(dict(
                    ChromeService=self.ChromeService
                )))

                self._webdriver = selenium.webdriver.Chrome(
                    service=self.ChromeService,
                    options=self.chrome_options
                )
                log.info(f'{self}')

                return self.webdriver

            self._webdriver = selenium.webdriver.Chrome(options=self.chrome_options)
            log.info(f'{self}')

            return self.webdriver
        except Exception as error:
            log.error(f'{error}')

    def set_chromedriver(self, chromedriver_path: str):
        log.debug(f'{chromedriver_path}')
        self._chromedriver_path = chromedriver_path
        self.update_paths()
        return self

    def set_locale(self, locale: str = 'en'):
        self.chrome_options.add_argument(f"--lang={locale}")
        log.debug(str(dict(
            add_argument=f"--lang={locale}"
        )))
        return self

    def set_locale_experimental(self, locale: str = 'en-US'):
        self.chrome_options.add_experimental_option(
            name='prefs',
            value={'intl.accept_languages': locale}
        )

        log.debug(str(dict(
            add_experimental_option=dict(
                name='prefs',
                value={'intl.accept_languages': locale}
            )
        )))
        return self

    def set_user_agent(self, user_agent: str):
        self.chrome_options.add_argument(f"user-agent={user_agent}")
        log.debug(str(dict(
            add_argument=f"user-agent={user_agent}"
        )))
        return self

    def set_window_size(self, *args, **kwargs):
        self._window_size = set_window_size(*args, **kwargs)
        width, height = self.window_size
        self.webdriver.set_window_size(width=width, height=height)
        log.debug(f'{width}, {height}')
        return self

    def start(self):
        """alias to run

        """
        return self.run()

    def stop_client(self):
        """stop client

        """
        result = self.webdriver.stop_client()
        log.info(f'{result}')
        return result

    def update_paths(self):
        if self.chromedriver_path:
            if self.chromedriver_path not in os.getenv('PATH'):
                os.environ['PATH'] = f"{os.getenv('PATH')}:{self._chromedriver_path}"
                log.debug(str(dict(
                    PATH=os.environ['PATH']
                )))

    def quit(self):
        """quit

        """
        result = self.webdriver.quit()
        log.info(f'{result}')
        return result

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
