import os
import sys
import warnings
import selenium
import selenium.webdriver

from automon import log
from automon.helpers.osWrapper.environ import environ_list

from .config_window_size import set_window_size

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


class ChromeWrapper(object):

    def __init__(self):
        self._webdriver = None
        self._chrome_options = selenium.webdriver.ChromeOptions()
        self._chromedriver_path = environ_list('SELENIUM_CHROMEDRIVER_PATH')
        self._ChromeService = None
        self._window_size = set_window_size()

        self.update_paths(self.chromedriver_path)

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
        for path in self._chromedriver_path:
            if os.path.exists(path):
                return path

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

    async def disable_certificate_verification(self):
        logger.warning('Certificates are not verified')
        self.chrome_options.add_argument('--ignore-certificate-errors')
        logger.debug(str(dict(
            add_argument='--ignore-certificate-errors'
        )))
        return self

    async def disable_extensions(self):
        self.chrome_options.add_argument("--disable-extensions")
        logger.debug(str(dict(
            add_argument=f'--disable-extensions'
        )))
        return self

    async def disable_infobars(self):
        self.chrome_options.add_argument("--disable-infobars")
        logger.debug(str(dict(
            add_argument=f'--disable-infobars'
        )))
        return self

    async def disable_notifications(self):
        """Pass the argument 1 to allow and 2 to block

        """
        self.chrome_options.add_experimental_option(
            "prefs", {"profile.default_content_setting_values.notifications": 2}
        )

        logger.debug(str(dict(
            add_experimental_option=("prefs", {"profile.default_content_setting_values.notifications": 2})
        )))
        return self

    async def disable_sandbox(self):
        self.chrome_options.add_argument('--no-sandbox')
        logger.debug(str(dict(
            add_argument=f'--no-sandbox'
        )))
        return self

    async def disable_shm(self):
        logger.warning('Disabled shm will use disk I/O, and will be slow')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        logger.debug(str(dict(
            add_argument=f'--disable-dev-shm-usage'
        )))
        return self

    async def enable_bigshm(self):
        logger.warning('Big shm not yet implemented')
        return self

    async def enable_defaults(self):
        await self.enable_maximized()
        return self

    async def enable_fullscreen(self):
        self.chrome_options.add_argument("--start-fullscreen")
        logger.debug(str(dict(
            add_argument=f'--start-fullscreen'
        )))
        return self

    async def enable_headless(self):
        self.chrome_options.add_argument('headless')
        logger.debug(str(dict(
            add_argument='headless'
        )))
        return self

    async def enable_notifications(self):
        """Pass the argument 1 to allow and 2 to block

        """
        self.chrome_options.add_experimental_option(
            "prefs", {"profile.default_content_setting_values.notifications": 1}
        )
        logger.debug(str(dict(
            add_experimental_option=("prefs", {"profile.default_content_setting_values.notifications": 1})
        )))
        return self

    async def enable_maximized(self):
        self.chrome_options.add_argument('--start-maximized')
        logger.debug(str(dict(
            add_argument='--start-maximized'
        )))
        return self

    async def enable_translate(self, native_language: str = 'en'):
        prefs = {
            "translate_whitelists": {"your native language": native_language},
            "translate": {"enabled": "True"}
        }
        self.chrome_options.add_experimental_option(
            name="prefs",
            value=prefs,
        )

        logger.debug(str(dict(
            add_experimental_option=dict(
                name="prefs",
                value=prefs,
            )
        )))
        return self

    async def close(self):
        """close

        """
        result = self.webdriver.close()
        logger.info(f'{result}')
        return result

    async def in_docker(self):
        """Chrome best used with docker

        """
        await self.enable_defaults()
        await self.enable_headless()
        await self.disable_sandbox()
        await self.disable_infobars()
        await self.disable_extensions()
        await self.disable_notifications()
        return self

    async def in_headless(self):
        """alias to headless sandboxed

        """
        return await self.in_headless_sandboxed()

    async def in_headless_sandboxed(self):
        """Headless Chrome with sandbox enabled

        """
        logger.warning(
            'Docker does not support sandbox option. '
            'Default shm size is 64m, which will cause chrome driver to crash.'
        )

        await self.enable_defaults()
        await self.enable_headless()
        return self

    async def in_headless_sandbox_disabled(self):
        """Headless Chrome with sandbox disabled

        """
        logger.warning('Default shm size is 64m, which will cause chrome driver to crash.')

        await self.enable_defaults()
        await self.enable_headless()
        await self.disable_sandbox()
        return self

    async def in_headless_sandbox_disabled_certificate_unverified(self):
        """Headless Chrome with sandbox disabled with no certificate verification

        """
        logger.warning('Default shm size is 64m, which will cause chrome driver to crash.')

        await self.enable_defaults()
        await self.enable_headless()
        await self.disable_sandbox()
        await self.disable_certificate_verification()
        return self

    async def in_headless_sandbox_disabled_shm_disabled(self):
        """Headless Chrome with sandbox disabled

        """
        await self.enable_defaults()
        await self.enable_headless()
        await self.disable_sandbox()
        await self.disable_shm()
        return self

    async def in_headless_sandbox_disabled_bigshm(self):
        """Headless Chrome with sandbox disabled

        """
        logger.warning('Larger shm option is not implemented')

        await self.enable_defaults()
        await self.enable_headless()
        await self.enable_bigshm()
        await self.disable_sandbox()
        return self

    async def in_remote_driver(self, host: str = '127.0.0.1', port: str = '4444', executor_path: str = '/wd/hub'):
        """Remote Selenium

        """
        logger.info(
            f'Remote WebDriver Hub URL: http://{host}:{port}{executor_path}/static/resource/hub.html')

        selenium.webdriver.Remote(
            command_executor=f'http://{host}:{port}{executor_path}',
            desired_capabilities=selenium.webdriver.common.desired_capabilities.DesiredCapabilities.CHROME
        )
        return self

    async def in_sandbox(self):
        """Chrome with sandbox enabled

        """
        logger.warning(
            'Docker does not support sandbox option. '
            'Default shm size is 64m, which will cause chrome driver to crash.'
        )

        await self.enable_defaults()
        return self

    async def in_sandbox_disabled(self):
        """Chrome with sandbox disabled

        """
        logger.warning('Default shm size is 64m, which will cause chrome driver to crash.')

        await self.enable_defaults()
        await self.disable_sandbox()
        return self

    async def run(self) -> selenium.webdriver.Chrome:
        try:
            if self.chromedriver_path:
                self._ChromeService = selenium.webdriver.ChromeService(
                    executable_path=self.chromedriver_path
                )
                logger.debug(str(dict(
                    ChromeService=self.ChromeService
                )))

                self._webdriver = selenium.webdriver.Chrome(
                    service=self.ChromeService,
                    options=self.chrome_options
                )
                logger.info(f'{self}')

                return self.webdriver

            self._webdriver = selenium.webdriver.Chrome(options=self.chrome_options)
            logger.info(f'{self}')

            return self.webdriver
        except Exception as error:
            logger.error(f'{error}')
            raise Exception(error)

    async def set_chromedriver(self, chromedriver_path: str):
        logger.debug(f'{chromedriver_path}')
        self._chromedriver_path.append(chromedriver_path)
        self.update_paths(chromedriver_path)
        return self

    async def set_locale(self, locale: str = 'en'):
        self.chrome_options.add_argument(f"--lang={locale}")
        logger.debug(str(dict(
            add_argument=f"--lang={locale}"
        )))
        return self

    async def set_locale_experimental(self, locale: str = 'en-US'):
        self.chrome_options.add_experimental_option(
            name='prefs',
            value={'intl.accept_languages': locale}
        )

        logger.debug(str(dict(
            add_experimental_option=dict(
                name='prefs',
                value={'intl.accept_languages': locale}
            )
        )))
        return self

    async def set_user_agent(self, user_agent: str):
        self.chrome_options.add_argument(f"user-agent={user_agent}")
        logger.debug(str(dict(
            add_argument=f"user-agent={user_agent}"
        )))
        return self

    async def set_window_size(self, *args, **kwargs):
        self._window_size = set_window_size(*args, **kwargs)
        width, height = self.window_size
        self.webdriver.set_window_size(width=width, height=height)
        logger.debug(f'{width}, {height}')
        return self

    async def start(self):
        """alias to run

        """
        return self.run()

    async def stop_client(self):
        """stop client

        """
        result = self.webdriver.stop_client()
        logger.info(f'{result}')
        return result

    def update_paths(self, path: str):
        if path and os.path.exists(path):
            if path not in os.getenv('PATH'):
                if sys.platform == 'win32':
                    os.environ['PATH'] = f"{os.getenv('PATH')};{path}"
                else:
                    os.environ['PATH'] = f"{os.getenv('PATH')}:{path}"

                logger.debug(str(dict(
                    SELENIUM_CHROMEDRIVER_PATH=path,
                    PATH=os.environ['PATH']
                )))

                return True

        logger.error(f'not found: {path}')

    async def quit(self):
        """quit

        """
        result = self.webdriver.quit()
        logger.info(f'{result}')
        return result

    async def quit_gracefully(self):
        """gracefully quit webdriver

        """
        try:
            await self.close()
            await self.quit()
            await self.stop_client()
        except Exception as error:
            logger.error(f'failed to gracefully quit. {error}')
            return False
        return True
