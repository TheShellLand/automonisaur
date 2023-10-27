import datetime

from automon.log import logger
from automon.integrations.seleniumWrapper import SeleniumBrowser

log = logger.logging.getLogger(__name__)
log.setLevel(logger.DEBUG)


class FacebookGroups(object):
    xpath_about = [
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[3]/div/div/div/div/div/div/div[1]/div/div/div/div/div[2]/a[1]/div[1]/span',
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[3]/div/div/div/div/div/div/div[1]/div/div/div/div/div[1]/div[1]/span',
    ]
    xpath_popup_close = [
        '/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/div/i',
    ]
    xpath_content_unavailble = [
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[1]/div[2]/div[1]/span',
    ]
    xpath_creation_date = [
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div[2]/div/div/div[4]/div/div/div/div/div/div[3]/div/div/div/div/div/div[2]/div/div[3]/div/div/div[2]/div/div/span',
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[3]/div/div/div/div/div/div[2]/div/div[3]/div/div/div[2]/div/div/span',
    ]
    xpath_history = [
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[1]/div/div/div/div/div/div[2]/div[4]/div/div/div[2]/div/div[2]/span/span',
    ]
    xpath_title = [
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[1]/div[2]/div/div/div/div/div[1]/div/div/div/div/div/div[1]/h1/span/a',
    ]
    xpath_members = [
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div[2]/div/div/div[4]/div/div/div/div/div/div[3]/div/div/div/div/div/div[2]/div/div[2]/div/div/div[2]/div/div[1]/span',
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[3]/div/div/div/div/div/div[2]/div/div[2]/div/div/div[2]/div/div[1]/span',
    ]
    xpath_posts_today = [
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[3]/div/div/div/div/div/div[2]/div/div[1]/div/div/div[2]/div/div[1]/span',
    ]
    xpath_posts_monthly = [
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[3]/div/div/div/div/div/div[2]/div/div[1]/div/div/div[2]/div/div[2]/span',
    ]
    xpath_privacy = [
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[1]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div/div[1]/span/span',
    ]
    xpath_privacy_details = [
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[1]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div/div[2]/span/span',
    ]
    xpath_visible = [
        '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div[1]/div/div/div/div/div/div[2]/div[3]/div/div/div[2]/div/div[2]/span/span',
    ]

    def __init__(self, url: str = None):
        """Facebook Groups object

        Depends on Selenium"""
        self._content_unavailable = None
        self._creation_date = None
        self._creation_date_timestamp = None
        self._history = None
        self._members = None
        self._members_count = None
        self._posts_monthly = None
        self._posts_monthly_count = None
        self._posts_today = None
        self._posts_today_count = None
        self._privacy = None
        self._privacy_details = None
        self._title = None
        self._url = url
        self._visible = None

        self._browser = None

    def __repr__(self):
        return f'{self.__dict__}'

    @property
    def content_unavailable(self):
        """This content isn't available right now"""
        if not self._browser:
            return

        if not self._content_unavailable:
            try:
                xpath_content_unavailble = self._browser.wait_for_xpath(self.xpath_content_unavailble)
                self._content_unavailable = self._browser.find_xpath(xpath_content_unavailble).text
            except Exception as error:
                message, session, stacktrace = self.error_parsing(error)
                log.error(str(dict(
                    url=self.url,
                    message=message,
                    session=session,
                    stacktrace=stacktrace,
                )))

        return self._content_unavailable

    @property
    def creation_date(self):
        if not self._browser:
            return

        if not self._creation_date:
            try:
                xpath_creation_date = self._browser.wait_for_xpath(self.xpath_creation_date)
                self._creation_date = self._browser.find_xpath(xpath_creation_date).text
            except Exception as error:
                message, session, stacktrace = self.error_parsing(error)
                log.error(str(dict(
                    url=self.url,
                    message=message,
                    session=session,
                    stacktrace=stacktrace,
                )))

        return self._creation_date

    @property
    def creation_date_timestamp(self):
        if self._creation_date:
            # TODO: convert date to datetime timestamp
            return self._creation_date_timestamp

    @property
    def history(self):
        if not self._browser:
            return

        if not self._history:
            try:
                xpath_history = self._browser.wait_for_xpath(self.xpath_history)
                self._history = self._browser.find_xpath(xpath_history).text
            except Exception as error:
                message, session, stacktrace = self.error_parsing(error)
                log.error(str(dict(
                    url=self.url,
                    message=message,
                    session=session,
                    stacktrace=stacktrace,
                )))

        return self._history

    @property
    def members(self):
        if not self._browser:
            return

        if not self._members:
            try:
                xpath_members = self._browser.wait_for_xpath(self.xpath_members)
                self._members = self._browser.find_xpath(xpath_members).text
                # TODO: need to clean up string from members and remove bad chars
            except Exception as error:
                message, session, stacktrace = self.error_parsing(error)
                log.error(str(dict(
                    url=self.url,
                    message=message,
                    session=session,
                    stacktrace=stacktrace,
                )))

        return self._members

    @property
    def members_count(self):
        if not self._browser:
            return

        if self._members:
            count = [x for x in self._members]
            count = [x for x in count if x in [str(x) for x in range(0, 10)]]
            if count:
                self._members_count = int(''.join(count)) if count else 0

        return self._members_count

    @property
    def posts_monthly(self):
        if not self._browser:
            return

        if not self._posts_monthly:
            try:
                xpath_monthly_posts = self._browser.wait_for_xpath(self.xpath_posts_monthly)
                self._posts_monthly = self._browser.find_xpath(xpath_monthly_posts).text
            except Exception as error:
                message, session, stacktrace = self.error_parsing(error)
                log.error(str(dict(
                    url=self.url,
                    message=message,
                    session=session,
                    stacktrace=stacktrace,
                )))

        return self._posts_monthly

    @property
    def posts_monthly_count(self):
        if not self._browser:
            return

        if self._posts_monthly:
            count = [x for x in self._posts_monthly]
            count = [x for x in count if x in [str(x) for x in range(0, 10)]]
            if count:
                self._posts_monthly_count = int(''.join(count)) if count else 0

        return self._posts_monthly_count

    @property
    def posts_today(self):
        if not self._browser:
            return

        if not self._posts_today:
            try:
                xpath_posts_today = self._browser.wait_for_xpath(self.xpath_posts_today)
                self._posts_today = self._browser.find_xpath(xpath_posts_today).text
            except Exception as error:
                message, session, stacktrace = self.error_parsing(error)
                log.error(str(dict(
                    url=self.url,
                    message=message,
                    session=session,
                    stacktrace=stacktrace,
                )))

        return self._posts_today

    @property
    def posts_today_count(self):
        if not self._browser:
            return

        if self.posts_today:
            count = [x for x in self.posts_today]
            count = [x for x in count if x in [str(x) for x in range(0, 10)]]
            if count:
                self._posts_today_count = int(''.join(count)) if count else 0

        return self._posts_today_count

    @property
    def privacy(self):
        if not self._browser:
            return

        if not self._privacy:
            try:
                xpath_privacy = self._browser.wait_for_xpath(self.xpath_privacy)
                self._privacy = self._browser.find_xpath(xpath_privacy).text
            except Exception as error:
                message, session, stacktrace = self.error_parsing(error)
                log.error(str(dict(
                    url=self.url,
                    message=message,
                    session=session,
                    stacktrace=stacktrace,
                )))

        return self._privacy

    @property
    def privacy_details(self):
        if not self._browser:
            return

        if not self._privacy_details:
            try:
                xpath_privacy_details = self._browser.wait_for_xpath(self.xpath_privacy_details)
                self._privacy_details = self._browser.find_xpath(xpath_privacy_details).text
            except Exception as error:
                message, session, stacktrace = self.error_parsing(error)
                log.error(str(dict(
                    url=self.url,
                    message=message,
                    session=session,
                    stacktrace=stacktrace,
                )))

        return self._privacy_details

    @property
    def title(self) -> str:
        if not self._browser:
            return

        if not self._title:
            try:
                xpath_title = self._browser.wait_for_xpath(self.xpath_title)
                self._title = self._browser.find_xpath(xpath_title).text
            except Exception as error:
                message, session, stacktrace = self.error_parsing(error)
                log.error(str(dict(
                    url=self.url,
                    message=message,
                    session=session,
                    stacktrace=stacktrace,
                )))

        return self._title

    @property
    def url(self) -> str:
        return self._url

    @property
    def visible(self) -> str:
        if not self._browser:
            return

        if not self._visible:
            try:
                xpath_visible = self._browser.wait_for_xpath(self.xpath_visible)
                self._visible = self._browser.find_xpath(xpath_visible).text
            except Exception as error:
                message, session, stacktrace = self.error_parsing(error)
                log.error(str(dict(
                    url=self.url,
                    message=message,
                    session=session,
                    stacktrace=stacktrace,
                )))

        return self._visible

    @staticmethod
    def error_parsing(error) -> tuple:
        error_parsed = f'{error}'.splitlines()
        error_parsed = [f'{x}'.strip() for x in error_parsed]
        message = error_parsed[0]
        session = error_parsed[1]
        stacktrace = error_parsed[2:]
        stacktrace = ' '.join(stacktrace)

        return message, session, stacktrace

    def get(self, url: str = None) -> bool:
        """get url"""
        if not self._browser:
            return

        if not url and not self.url:
            log.error(f'missing url')
            raise Exception(f"missing url")

        get = self._browser.get(url=url or self.url)
        log.info(f'{url} {get}')
        return get

    def get_about(self):
        url = f'{self.url}/about'
        log.debug(f'{url}')
        get = self.get(url=url)
        log.info(f'{url} {get}')
        return get

    def run(self):
        """run selenium browser"""
        if self._browser:
            log.info(f'{self._browser}')
            return self._browser.run()

    def restart(self):
        """quit and start new instance of selenium"""
        if self._browser:
            self.quit()
        log.info(f'{self._browser}')
        return self.start()

    def start(self, headless: bool = True):
        """start new instance of selenium"""
        self._browser = SeleniumBrowser()

        if headless:
            self._browser.set_webdriver().Chrome().in_headless().set_locale_experimental()
        else:
            self._browser.set_webdriver().Chrome().set_locale_experimental()

        self._browser.set_webdriver().Chrome().set_user_agent(
            self._browser.get_random_user_agent()
        )

        log.info(f'{self._browser}')
        return self._browser.run()

    def stop(self):
        """alias to quit"""
        return self.quit()

    def to_dict(self):
        return dict(
            content_unavailable=self.content_unavailable,
            creation_date=self.creation_date,
            creation_date_timestamp=self.creation_date_timestamp,
            history=self.history,
            members=self.members,
            members_count=self.members_count,
            posts_monthly=self.posts_monthly,
            posts_monthly_count=self.posts_monthly_count,
            posts_today=self.posts_today,
            posts_today_count=self.posts_today_count,
            privacy=self.privacy,
            privacy_details=self.privacy_details,
            title=self.title,
            url=self.url,
            visible=self.visible,
            status=self._browser.request_status,
        )

    def quit(self):
        """quit selenium"""
        if self._browser:
            log.info(f'{self._browser}')
            return self._browser.quit()
