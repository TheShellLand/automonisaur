import os
import io
import warnings
import datetime

from selenium import webdriver
from urllib.parse import urlparse
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from automon.log.logger import Logging
from automon.helpers.sleeper import Sleeper
from automon.helpers.sanitation import Sanitation
from automon.integrations.minio import use_public_server
from automon.integrations.selenium import options
from automon.integrations.selenium.actions import Actions

log = Logging(name='selenium', level=Logging.INFO)


class Browser:

    def __init__(self, browser=None, webdriver=webdriver):
        self._log = Logging(name=Browser.__name__, level=Logging.DEBUG)

        self.webdriver = webdriver
        self.browser = browser if browser else self.webdriver.Chrome()
        self.minio_client = None

    def set_minio_client(self, minio_client):
        self.minio_client = minio_client

    def save_screenshot_to_minio(self, url=None, bucket_name='screenshots', object_name=None, prefix=None):

        if not self.minio_client:
            return False

        if url:
            self.browser.get(url)

        if not object_name:
            object_name = screenshot_name(self.browser, prefix)

        Sleeper.seconds('Loading page', 4)

        bucket_name = bucket_name
        object_name = object_name
        data = io.BytesIO(self.browser.get_screenshot_as_png())
        length = data.getvalue().__len__()

        private_minio = self.minio_client
        private_minio.make_bucket(bucket_name)

        return private_minio.put_object(bucket_name, object_name, data, length)

    def save_screenshot_to_public_minio(self, url=None, bucket_name='mymymymymyscreenshots', object_name=None,
                                        prefix=None):

        if url:
            self.browser.get(url)
            Sleeper.seconds('Loading page', 4)

        if not object_name:
            object_name = screenshot_name(self.browser, prefix)

        png = self.browser.get_screenshot_as_png()

        bucket_name = bucket_name
        object_name = object_name
        data = io.BytesIO(png)
        length = data.getvalue().__len__()

        public_minio = use_public_server()
        public_minio.make_bucket(bucket_name)

        return public_minio.put_object(bucket_name, object_name, data, length)

    def save_screenshot_to_file(self, url=None, object_name=None, prefix=None):

        if url:
            self.browser.get(url)
            Sleeper.seconds('Loading page', 4)

        if not object_name:
            object_name = screenshot_name(self.browser, prefix)

        path = os.path.abspath('/tmp/hev')
        if not os.path.exists(path):
            os.makedirs(path)

        return self.browser.save_screenshot(os.path.join(path, object_name))

    def new_resolution(self, width=1920, height=1080, device_type='web'):

        if device_type == 'pixel3':
            width = 1080
            height = 2160

        if device_type == 'web-small' or device_type == '800x600':
            width = 800
            height = 600

        if device_type == 'web-small-2' or device_type == '1024x768':
            width = 1024
            height = 768

        if device_type == 'web-small-3' or device_type == '1280x960':
            width = 1280
            height = 960

        if device_type == 'web-small-4' or device_type == '1280x1024':
            width = 1280
            height = 1024

        if device_type == 'web' or device_type == '1920x1080':
            width = 1920
            height = 1080

        if device_type == 'web-2' or device_type == '1600x1200':
            width = 1600
            height = 1200

        if device_type == 'web-3' or device_type == '1920x1200':
            width = 1920
            height = 1200

        if device_type == 'web-large' or device_type == '2560x1400':
            width = 2560
            height = 1400

        if device_type == 'web-long' or device_type == '1920x3080':
            width = 1920
            height = 3080

        self.browser.set_window_size(width, height)

    def close(self):
        self.browser.close()

    def quit(self):
        self.browser.close()
        self.browser.quit()
        self.browser.stop_client()


def chrome():
    """Chrome with no options

    """
    warnings.warn('Docker does not support sandbox option')
    warnings.warn('Default shm size is 64m, which will cause chrome driver to crash.', Warning)

    opt = options.default(webdriver.ChromeOptions())

    return webdriver.Chrome(options=opt)


def chrome_for_docker():
    """Chrome best used with docker

    """
    opt = options.default(webdriver.ChromeOptions())
    opt = options.nosandbox(opt)
    opt = options.headless(opt)
    opt = options.noinfobars(opt)
    opt = options.noextensions(opt)
    opt = options.nonotifications(opt)

    return webdriver.Chrome(options=opt)


def chrome_sandboxed():
    """Chrome with sandbox enabled

    """
    warnings.warn('Docker does not support sandbox option')
    warnings.warn('Default shm size is 64m, which will cause chrome driver to crash.', Warning)

    opt = options.default(webdriver.ChromeOptions())

    return webdriver.Chrome(options=opt)


def chrome_nosandbox():
    """Chrome with sandbox disabled

    """
    warnings.warn('Default shm size is 64m, which will cause chrome driver to crash.', Warning)

    opt = options.default(webdriver.ChromeOptions())
    opt = options.nosandbox(opt)

    return webdriver.Chrome(options=opt)


def chrome_headless_sandboxed():
    """Headless Chrome with sandbox enabled

    """
    warnings.warn('Docker does not support sandbox option')
    warnings.warn('Default shm size is 64m, which will cause chrome driver to crash.', Warning)

    opt = options.default(webdriver.ChromeOptions())
    opt = options.headless(opt)

    return webdriver.Chrome(options=opt)


def chrome_headless_nosandbox():
    """Headless Chrome with sandbox disabled

    """
    warnings.warn('Default shm size is 64m, which will cause chrome driver to crash.', Warning)

    opt = options.default(webdriver.ChromeOptions())
    opt = options.headless(opt)
    opt = options.nosandbox(opt)

    return webdriver.Chrome(options=opt)


def chrome_headless_nosandbox_unsafe():
    """Headless Chrome with sandbox disabled with not certificate verification

    """
    warnings.warn('Default shm size is 64m, which will cause chrome driver to crash.', Warning)

    opt = options.default(webdriver.ChromeOptions())
    opt = options.headless(opt)
    opt = options.nosandbox(opt)
    opt = options.unsafe(opt)

    return webdriver.Chrome(options=opt)


def chrome_headless_nosandbox_noshm():
    """Headless Chrome with sandbox disabled

    """
    opt = options.default(webdriver.ChromeOptions())
    opt = options.headless(opt)
    opt = options.nosandbox(opt)
    opt = options.noshm(opt)

    return webdriver.Chrome(options=opt)


def chrome_headless_nosandbox_bigshm():
    """Headless Chrome with sandbox disabled

    """
    warnings.warn('Larger shm option is not implemented', Warning)

    opt = options.default(webdriver.ChromeOptions())
    opt = options.headless(opt)
    opt = options.nosandbox(opt)
    opt = options.bigshm(opt)

    return webdriver.Chrome(options=opt)


def chrome_remote(host='127.0.0.1', port='4444', executor_path='/wd/hub'):
    """Remote Selenium

    """
    log.info(
        'Remote WebDriver Hub URL: http://{}:{}{}/static/resource/hub.html'.format(host, port, executor_path))

    return webdriver.Remote(
        command_executor='http://{}:{}{}'.format(host, port, executor_path),
        desired_capabilities=DesiredCapabilities.CHROME
    )


def screenshot_name(browser, prefix=None):
    """Generate a unique filename

    :param browser:
    :param prefix: prefix filename with a string
    :return:
    """
    title = browser.title
    url = browser.current_url
    hostname = urlparse(url).hostname

    hostname_ = Sanitation.ascii_numeric_only(hostname)
    title_ = Sanitation.ascii_numeric_only(title)
    timestamp = str(datetime.datetime.now().isoformat()).replace(':', '_')

    if prefix:
        prefix = Sanitation.safe_string(prefix)
        return '{}_{}_{}_{}{}'.format(prefix, hostname_, title_, timestamp, '.png')

    return '{}_{}_{}{}'.format(hostname_, title_, timestamp, '.png')


if __name__ == "__main__":
    browser = chrome()
    browser.close()
    browser.quit()
