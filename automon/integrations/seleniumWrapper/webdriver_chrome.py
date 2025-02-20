import os
import sys
import selenium
import selenium.webdriver
import automon.helpers.subprocessWrapper

from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO
from automon.helpers.osWrapper import environ_list
from automon.integrations.seleniumWrapper.user_agents import SeleniumUserAgentBuilder

from .config_window_size import set_window_size

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


class ChromeWrapper(object):

    def __init__(self):
        self._webdriver = None
        self._chrome_options = selenium.webdriver.ChromeOptions()
        self._chromedriver_path = environ_list('SELENIUM_CHROMEDRIVER_PATH')
        self._ChromeService = None
        self._window_size = set_window_size()
        self._enable_antibot_detection = None
        self._service_args = []

    def __repr__(self):
        if self._webdriver:
            return str(dict(
                name=self.webdriver.name,
                session_id=self.session_id,
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
        for path in self._chromedriver_path:
            if os.path.exists(path):
                logger.debug(
                    f'[ChromeWrapper] :: '
                    f'chromedriver_path :: '
                    f'{path=}'
                )
                return path

        check_bin = automon.helpers.subprocessWrapper.Run(command='which chromedriver').stdout.decode().strip()

        if check_bin:
            logger.debug(
                f'[ChromeWrapper] :: '
                f'chromedriver_path :: '
                f'{check_bin=}'
            )
            return check_bin

        raise Exception('missing SELENIUM_CHROMEDRIVER_PATH')

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

    def disable_automation_switch(self):
        """exclude the collection of enable-automation switches

        """
        logger.warning(f'[ChromeWrapper] :: disable_automation_switch :: {DeprecationWarning}')

        self.chrome_options.add_experimental_option(
            "excludeSwitches", ["enable-automation"]
        )
        logger.debug(
            f'[ChromeWrapper] :: '
            f'add_experimental_option :: '
            f'{dict(name="excludeSwitches", value=["enable-automation"])}'
        )

        return self

    def disable_AutomationControlled(self):
        """adding argument to disable the AutomationControlled flag

        """
        logger.debug(f'[ChromeWrapper] :: add_argument :: --disable-blink-features=AutomationControlled')
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        return self

    def disable_certificate_verification(self):
        logger.debug(f'[ChromeWrapper] :: add_argument :: --ignore-certificate-errors')
        logger.warning(f'[ChromeWrapper] :: disable_certificate_verification :: Certificates are not verified')
        self.chrome_options.add_argument('--ignore-certificate-errors')
        return self

    def disable_extensions(self):
        logger.debug(f'[ChromeWrapper] :: add_argument :: --disable-extensions')
        self.chrome_options.add_argument("--disable-extensions")
        return self

    def disable_infobars(self):
        logger.debug(f'[ChromeWrapper] :: add_argument :: --disable-infobars')
        self.chrome_options.add_argument("--disable-infobars")
        return self

    def disable_javascript_webdriver_prop(self):
        """changing the property of the navigator value for webdriver to undefined

        """
        self.webdriver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return self

    def disable_notifications(self):
        """Pass the argument 1 to allow and 2 to block

        """
        self.chrome_options.add_experimental_option(
            "prefs", {"profile.default_content_setting_values.notifications": 2}
        )

        logger.debug(
            f'[ChromeWrapper] :: '
            f'add_experimental_option :: '
            f'{dict(name="prefs", value={"profile.default_content_setting_values.notifications": 2})}'
        )

        return self

    def disable_sandbox(self):
        logger.debug(f'[ChromeWrapper] :: add_argument :: --no-sandbox')
        self.chrome_options.add_argument('--no-sandbox')
        return self

    def disable_shm(self):
        logger.warning('[ChromeWrapper] :: disable_shm :: Disabled shm will use disk I/O, and will be slow')
        logger.debug(f'[ChromeWrapper] :: add_argument :: --disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        return self

    def disable_userAutomationExtension(self):
        """turn-off userAutomationExtension

        """
        self.chrome_options.add_experimental_option(
            "useAutomationExtension", False
        )
        logger.debug(
            f'[ChromeWrapper] :: '
            f'add_experimental_option :: '
            f'{dict(name="useAutomationExtension", value=False)}'
        )

        return self

    def download_chromedriver(self):
        versions = 'https://googlechromelabs.github.io/chrome-for-testing/latest-versions-per-milestone-with-downloads.json'
        raise

    def enable_antibot_detection(self):
        """Disabling the Automation Indicator WebDriver Flags

        """
        self.disable_AutomationControlled()
        self.disable_automation_switch()
        self.disable_userAutomationExtension()

        useragent = SeleniumUserAgentBuilder().get_top()
        self.set_user_agent(useragent)

        self._enable_antibot_detection = True
        return self

    def enable_bigshm(self):
        logger.warning('[ChromeWrapper] :: enable_bigshm :: Big shm not yet implemented')
        return self

    def enable_defaults(self):
        self.enable_maximized()
        self.enable_logging()
        self.set_logging_level(level='ALL')
        return self

    def enable_fullscreen(self):
        logger.debug(f'[ChromeWrapper] :: add_argument :: --start-fullscreen')
        self.chrome_options.add_argument("--start-fullscreen")
        return self

    def enable_headless(self):
        logger.debug(f'[ChromeWrapper] :: add_argument :: headless')
        self.chrome_options.add_argument('headless')
        return self

    def enable_logging(self):
        logger.debug(f'[ChromeWrapper] :: set_capability :: "goog:loggingPrefs", {{"performance": "ALL"}}')
        self.chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        return self

    def enable_notifications(self):
        """Pass the argument 1 to allow and 2 to block

        """
        self.chrome_options.add_experimental_option(
            "prefs", {"profile.default_content_setting_values.notifications": 1}
        )
        logger.debug(
            f'[ChromeWrapper] :: '
            f'add_experimental_option :: '
            f'{dict(name="prefs", value={"profile.default_content_setting_values.notifications": 1})}'
        )

        return self

    def enable_maximized(self):
        logger.debug(f'[ChromeWrapper] :: add_argument :: --start-maximized')
        self.chrome_options.add_argument('--start-maximized')
        return self

    def enable_proxy(self, proxy: str):
        logger.debug(f'[ChromeWrapper] :: add_argument :: --proxy-server={proxy}')
        self.chrome_options.add_argument(f"--proxy-server={proxy}")
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

        logger.debug(
            f'[ChromeWrapper] :: '
            f'add_experimental_option :: '
            f'{dict(name="prefs", value=prefs)}'
        )

        return self

    def close(self):
        """close

        """
        result = self.webdriver.close()
        logger.info(f'[ChromeWrapper] :: close :: {result}')
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
        logger.warning(
            '[ChromeWrapper] :: in_headless_sandboxed :: '
            'Docker does not support sandbox option. '
            'Default shm size is 64m, which will cause chrome driver to crash.'
        )

        self.enable_defaults()
        self.enable_headless()
        return self

    def in_headless_sandbox_disabled(self):
        """Headless Chrome with sandbox disabled

        """
        logger.warning(
            f'[ChromeWrapper] :: in_headless_sandbox_disabled :: '
            f'Default shm size is 64m, which will cause chrome driver to crash.'
        )

        self.enable_defaults()
        self.enable_headless()
        self.disable_sandbox()
        return self

    def in_headless_sandbox_disabled_certificate_unverified(self):
        """Headless Chrome with sandbox disabled with no certificate verification

        """
        logger.warning(
            f'[ChromeWrapper] :: '
            f'in_headless_sandbox_disabled_certificate_unverified :: '
            f'Default shm size is 64m, which will cause chrome driver to crash.'
        )

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
        logger.warning(
            f'[ChromeWrapper] :: '
            f'in_headless_sandbox_disabled_bigshm :: '
            f'Larger shm option is not implemented'
        )

        self.enable_defaults()
        self.enable_headless()
        self.enable_bigshm()
        self.disable_sandbox()
        return self

    def in_remote_driver(self, host: str = '127.0.0.1', port: str = '4444', executor_path: str = '/wd/hub'):
        """Remote Selenium

        """
        logger.info(
            f'Remote WebDriver Hub URL: http://{host}:{port}{executor_path}/static/resource/hub.html')

        selenium.webdriver.Remote(
            command_executor=f'http://{host}:{port}{executor_path}',
            desired_capabilities=selenium.webdriver.common.desired_capabilities.DesiredCapabilities.CHROME
        )
        return self

    def in_sandbox(self):
        """Chrome with sandbox enabled

        """
        logger.warning(
            '[ChromeWrapper] :: in_sandbox :: '
            'Docker does not support sandbox option. '
            'Default shm size is 64m, which will cause chrome driver to crash.'
        )

        self.enable_defaults()
        return self

    def in_sandbox_disabled(self):
        """Chrome with sandbox disabled

        """
        logger.warning(
            '[ChromeWrapper] :: '
            'in_sandbox_disabled :: '
            'Default shm size is 64m, which will cause chrome driver to crash.'
        )

        self.enable_defaults()
        self.disable_sandbox()
        return self

    def run(self) -> bool:
        chromedriver_path = self.chromedriver_path

        if chromedriver_path:
            self.update_paths(chromedriver_path)

            self._ChromeService = selenium.webdriver.ChromeService(
                executable_path=chromedriver_path,
                service_args=self.service_args
            )
        else:
            self._ChromeService = None

        logger.debug(f'[ChromeWrapper] :: run :: {self.ChromeService=}')

        try:
            self._webdriver = selenium.webdriver.Chrome(
                service=self.ChromeService,
                options=self.chrome_options
            )

            if self._enable_antibot_detection:
                self.disable_javascript_webdriver_prop()

            logger.debug(f'[ChromeWrapper] :: run :: {self=}')
            logger.info(f'[ChromeWrapper] :: run :: done')
            return True

        except Exception as error:
            raise Exception(f'[ChromeWrapper] :: run :: failed :: {error=}')

    @property
    def service_args(self):
        return self._service_args

    @property
    def session_id(self):
        if self.webdriver:
            return self.webdriver.session_id

    def set_logging_level(self, level: str = 'ALL'):
        """There are 6 available log levels: ALL, DEBUG, INFO, WARNING, SEVERE, and OFF.
        Note that --verbose is equivalent to --log-level=ALL and --silent is equivalent
        to --log-level=OFF, so this example is just setting the log level generically

        """
        logger.debug(f'[ChromeWrapper] :: service_args :: {level}')
        self.service_args.append(f'--log-level={level.upper()}')
        return self

    def set_chromedriver(self, chromedriver_path: str):
        logger.debug(f'[ChromeWrapper] :: {chromedriver_path=}')
        self._chromedriver_path.append(chromedriver_path)
        self.update_paths(chromedriver_path)
        return self

    def set_locale(self, locale: str = 'en'):
        logger.debug(f'[ChromeWrapper] :: add_argument :: "--lang={locale}"')
        self.chrome_options.add_argument(f"--lang={locale}")
        return self

    def set_locale_experimental(self, locale: str = 'en-US'):
        self.chrome_options.add_experimental_option(
            name='prefs',
            value={'intl.accept_languages': locale}
        )

        logger.debug(
            f'[ChromeWrapper] :: '
            f'add_experimental_option :: '
            f"{dict(name='prefs', value={'intl.accept_languages': locale})}"
        )

        return self

    def set_user_agent(self, user_agent: str):
        logger.debug(f'[ChromeWrapper] :: add_argument :: f"user-agent={user_agent}"')
        self.chrome_options.add_argument(f"user-agent={user_agent}")
        return self

    def set_user_data_dir(self, user_data_dir: str = None):
        if user_data_dir is None:
            user_data_dir = automon.Tempfile.mkdtemp()

        logger.debug(f'[ChromeWrapper] :: add_argument :: f"user-data-dir={user_data_dir}"')
        self.chrome_options.add_argument(f"user-data-dir={user_data_dir}")
        return self

    def set_window_size(self, *args, **kwargs):
        """has to be set after setting webdriver"""
        logger.debug(f'[ChromeWrapper] :: set_window_size :: {args=} :: {kwargs=}')
        self._window_size = set_window_size(*args, **kwargs)
        width, height = self.window_size
        self.webdriver.set_window_size(width=width, height=height)
        logger.info(f'[ChromeWrapper] :: set_window_size :: {width=} {height=}')
        return self

    def start(self):
        """alias to run

        """
        return self.run()

    def stop_client(self):
        """stop client

        """
        result = self.webdriver.stop_client()
        logger.info(f'[ChromeWrapper] :: stop_client :: {result=}')
        return result

    def update_paths(self, path: str):
        if path and os.path.exists(path):
            if path not in os.getenv('PATH'):
                if sys.platform == 'win32':
                    os.environ['PATH'] = f"{os.getenv('PATH')};{path}"
                else:
                    os.environ['PATH'] = f"{os.getenv('PATH')}:{path}"

                # logger.debug(f'update_paths :: {path=} :: {os.environ['PATH']}')
                logger.debug(f'[ChromeWrapper] :: update_paths :: {path=}')

                logger.info(f'[ChromeWrapper] :: update_paths :: done')
                return True
            else:
                return True

        logger.error(f'[ChromeWrapper] :: update_paths :: failed :: {path} not found')
        return False

    def quit(self):
        """quit

        """
        result = self.webdriver.quit()
        logger.info(f'[ChromeWrapper] :: quit :: {result}')
        return result

    def quit_gracefully(self):
        """gracefully quit webdriver

        """
        try:
            self.close()
            self.quit()
            self.stop_client()
        except Exception as error:
            logger.error(f'[ChromeWrapper] :: quit :: error :: failed to gracefully quit. {error}')
            return False
        return True
