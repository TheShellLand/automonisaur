import bs4
import json
import threading
import requests
import requests.adapters

import automon.integrations.seleniumWrapper.user_agents

from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO
from .config import RequestsConfig

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


class RequestsClient(object):
    def __init__(self, url: str = None, data: dict = None, headers: dict = {},
                 config: RequestsConfig = None):
        """Wrapper for requests library"""

        self.config = config or RequestsConfig()

        self._thread_local = threading.local()

        self.url: str = url
        self.data: any = data
        self.errors: bytes = b''
        self.response = None
        self.requests = requests
        self.proxies = self.config.get_proxy()

        self.headers = headers or {}

        self._bs4 = bs4.BeautifulSoup

    def __repr__(self):
        return f'{self.__dict__}'

    def __len__(self):
        if self.content:
            len(self.content)

    def __bool__(self):
        if self.response:
            if self.response.status_code == 200:
                return True
        return False

    def _get_session(self) -> requests.Session:
        """Gets the current thread's dedicated requests.Session."""
        if not hasattr(self._thread_local, "session"):
            session = requests.Session()
            session.headers.update(self.headers)
            # Create a brand new session object only if this thread doesn't have one yet
            self._thread_local.session = session
        return self._thread_local.session

    @property
    def session(self) -> requests.Session:
        return self._get_session()

    def _log_result(self):
        if self.status_code == 200:
            msg = [
                '[RequestsClient]',
                self.response.request.method,
                f'{self.status_code}',
                f'{self.response.url}',
                f'{self.proxies=}',
                f'{round(len(self.content) / 1024, 2)} KB',
            ]
            msg = ' :: '.join([str(x) for x in msg])
            return logger.debug(msg)

        msg = [
            '[RequestsClient]',
            self.response.request.method,
            f'{self.status_code}',
            f'{self.response.url}',
            f'{self.proxies=}',
            f'{round(len(self.content) / 1024, 2)} KB',
            f'{self.content=}'
        ]

        msg = ' :: '.join([str(x) for x in msg])
        return logger.error(msg)

    def _params(self, url, data, headers):
        if url is None:
            url = self.url

        if data is None:
            data = self.data

        if headers is None:
            headers = self.headers

        self.url = url
        self.data = data
        self.headers = headers
        return url, data, headers

    @property
    def content(self):
        if hasattr(self.response, 'content'):
            return self.response.content

    @property
    def content_bs4(self):
        if self.content:
            return self._bs4(self.content)

    def content_to_dict(self):
        return self.to_dict()

    def _set_retry(self, max_retries: int = None, **kwargs):

        if max_retries is None:
            retries = self.requests.adapters.Retry(total=max_retries,
                                                   backoff_factor=0.1,
                                                   **kwargs)
        else:
            retries = self.requests.adapters.Retry(total=max_retries,
                                                   backoff_factor=0.1,
                                                   status_forcelist=[500, 502, 503, 504],
                                                   **kwargs)

        adapter = requests.adapters.HTTPAdapter(max_retries=retries)

        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        return self

    def set_global_retry(self, max_retries: int, **kwargs):
        return self._set_retry(max_retries=max_retries, **kwargs)

    def set_user_agent(self, user_agent: str):
        self.update_headers({'User-Agent': user_agent})
        return self

    def set_random_user_agent(self):
        self.set_user_agent(
            user_agent=automon.integrations.seleniumWrapper.user_agents.SeleniumUserAgentBuilder().get_top())
        return self

    def _set_proxy(self):
        if self.config.proxies:
            if self.config.use_random_proxies:
                self.proxies = self.config.get_random_proxy()
            else:
                self.proxies = self.config.get_proxy()

        logger.debug(f'[RequestsClient] :: SET PROXY :: {self.proxies}')
        return self

    def delete(
            self,
            url: str = None,
            data: dict = None,
            headers: dict = None,
            max_retries: int = 5,
            **kwargs
    ) -> bool:
        """requests.delete"""

        url, data, headers = self._params(url, data, headers)
        self._set_retry(max_retries=max_retries)
        self._set_proxy()

        logger.debug(f'[RequestsClient] :: DELETE :: {url=} :: {data=} :: {headers=} :: {self.proxies=} :: {kwargs=}')

        try:
            self.response = self.session.delete(url=url, data=data, headers=headers, proxies=self.proxies, **kwargs)
            self._log_result()

            if self.status_code == 200:
                return True

        except Exception as error:
            self.errors = error
            raise Exception(f'[RequestsClient] :: DELETE :: ERROR :: {error=}')
        return False

    def delete_self(self, *args, **kwargs):
        self.delete(*args, **kwargs)
        return self

    def get(
            self,
            url: str = None,
            data: dict = None,
            headers: dict = None,
            max_retries: int = None,
            **kwargs
    ) -> bool:
        """requests.get"""

        url, data, headers = self._params(url, data, headers)
        self._set_retry(max_retries=max_retries)
        self._set_proxy()

        logger.debug(f'[RequestsClient] :: GET :: {url=} :: {data=} :: {headers=} :: {self.proxies=} :: {kwargs=}')

        try:
            self.response = self.session.get(url=url, data=data, headers=headers, proxies=self.proxies, **kwargs)
            self._log_result()

            if self.status_code == 200:
                return True

            self.errors = self.content

        except Exception as error:
            self.errors = error
            raise Exception(f'[RequestsClient] :: GET :: ERROR :: {error=}')
        return False

    def get_self(self, *args, **kwargs):
        self.get(*args, **kwargs)
        return self

    def patch(
            self,
            url: str = None,
            data: dict = None,
            headers: dict = None,
            max_retries: int = None,
            **kwargs
    ) -> bool:
        """requests.patch"""

        url, data, headers = self._params(url, data, headers)
        self._set_retry(max_retries=max_retries)
        self._set_proxy()

        logger.debug(f'[RequestsClient] :: PATCH :: {url=} :: {data=} :: {headers=} :: {self.proxies=} :: {kwargs=}')

        try:
            self.response = self.session.patch(url=url, data=data, headers=headers, proxies=self.proxies, **kwargs)
            self._log_result()

            if self.status_code == 200:
                return True

            self.errors = self.content

        except Exception as error:
            self.errors = error
            raise Exception(f'[RequestsClient] :: PATCH :: ERROR :: {error=}')
        return False

    def patch_self(self, *args, **kwargs):
        self.patch(*args, **kwargs)
        return self

    def post(
            self,
            url: str = None,
            data: any = None,
            headers: dict = None,
            max_retries: int = None,
            **kwargs
    ) -> bool:
        """requests.post"""

        url, data, headers = self._params(url, data, headers)
        self._set_retry(max_retries=max_retries)
        self._set_proxy()

        logger.debug(f'[RequestsClient] :: POST :: {url=} :: {data=} :: {headers=} :: {self.proxies=} :: {kwargs=}')

        try:
            self.response = self.session.post(url=url, data=data, headers=headers, proxies=self.proxies, **kwargs)
            self._log_result()

            if self.status_code == 200:
                return True

            self.errors = self.content

        except Exception as error:
            self.errors = error
            raise Exception(f'[RequestsClient] :: POST :: ERROR :: {error=}')
        return False

    def post_self(self, *args, **kwargs):
        self.post(*args, **kwargs)
        return self

    def put(
            self,
            url: str = None,
            data: dict = None,
            headers: dict = None,
            max_retries: int = None,
            **kwargs
    ) -> bool:
        """requests.put"""

        url, data, headers = self._params(url, data, headers)
        self._set_retry(max_retries=max_retries)
        self._set_proxy()

        logger.debug(f'[RequestsClient] :: PUT :: {url=} :: {data=} :: {headers=} :: {self.proxies=} :: {kwargs=}')

        try:
            self.response = self.session.put(url=url, data=data, headers=headers, proxies=self.proxies, **kwargs)
            self._log_result()

            if self.status_code == 200:
                return True

            self.errors = self.content

        except Exception as error:
            self.errors = error
            raise Exception(f'[RequestsClient] :: PUT :: ERROR :: {error=}')
        return False

    def put_self(self, *args, **kwargs):
        self.put(*args, **kwargs)
        return self

    @property
    def reason(self):
        if 'reason' in dir(self.response):
            return self.response.reason

    @property
    def status_code(self):
        if 'status_code' in dir(self.response):
            return self.response.status_code

    @property
    def text(self) -> str:
        if self.response:
            return self.response.text
        return ''

    @property
    def _to_dict(self):
        return self.to_dict()

    def to_dict(self) -> dict:
        if self.response is not None:
            try:
                return json.loads(self.content)
            except Exception as error:
                raise Exception(f'[RequestsClient] :: TO DICT :: ERROR :: {error=}')
        return {}

    def to_json(self) -> str:
        if self.content:
            try:
                return json.dumps(json.loads(self.content))
            except Exception as error:
                raise Exception(f'[RequestsClient] :: TO JSON :: ERROR :: {error=}')
        return ''

    def update_headers(self, headers: dict):
        return self.headers.update(headers)
