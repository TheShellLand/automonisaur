import bs4
import json
import pandas
import threading
import requests
import requests.adapters

import automon.integrations.seleniumWrapper.user_agents

from automon.helpers import *
from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO

from .config import RequestsConfig

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


class RequestResponse(DictHelper):
    content: bytes
    reason: str
    request: object
    text: str
    url: str

    _bs4: bs4.BeautifulSoup

    def __init__(self, response=None):

        self.request = None

        self._content = None
        self._status_code = None
        self._reason = None
        self._url = None

        self._bs4 = bs4.BeautifulSoup

        super().__init__(response)

        self._log_result()

        if not self:
            _raw_data = self._raw_data
            raise debug_exception(locals(), f'request failed')

    def __bool__(self):
        if self.status_code == 200:
            return True
        return False

    def _log_result(self):
        if self.status_code == 200:
            msg = [
                '[RequestResponse]',
                self.request.method,
                f'{self.status_code}',
                f'{self.url}',
                f'{round(len(self.content) / 1024, 2)} KB',
            ]
            msg = ' :: '.join([str(x) for x in msg])
            return logger.debug(msg)

        else:
            msg = [
                '[RequestResponse]',
                self.request.method,
                f'{self.status_code}',
                f'{self.url}',
                f'{round(len(self.content) / 1024, 2)} KB',
                f'{self.content=}'
            ]
            msg = ' :: '.join([str(x) for x in msg])

        return Exception(msg)

    @property
    def content(self) -> bytes:
        return self._content

    @content.setter
    def content(self, content):
        self._content = content

    @property
    def content_bs4(self):
        if self.content is not None:
            return self._bs4(self.content)

    @property
    def content_df(self):
        try:
            return pandas.DataFrame(self.to_dict())
        except:
            pass

    def content_to_dict(self):
        return self.to_dict()

    @property
    def reason(self):
        return self._reason

    @reason.setter
    def reason(self, value):
        self._reason = value

    @property
    def status_code(self):
        return self._status_code

    @status_code.setter
    def status_code(self, value):
        self._status_code = value

    @property
    def text(self) -> str:
        return self.content.decode('utf-8')

    @property
    def url(self) -> str:
        return self._url

    @url.setter
    def url(self, value):
        self._url = value

    def to_dict(self):
        return json.loads(self.content)

    def to_json(self) -> str:
        return json.dumps(json.loads(self.content))


class RequestsClient(object):
    def __init__(self, url: str = None, data: dict = None, headers: dict = {},
                 config: RequestsConfig = None):
        """Wrapper for requests library"""

        self.config = config or RequestsConfig()

        self._thread_local = threading.local()

        self.url: str = url
        self.data: any = data
        self.response = None
        self.requests = requests
        self.proxies = self.config.get_proxy()

        self.headers = headers or {}

        self._bs4 = bs4.BeautifulSoup

    def __repr__(self):
        return f'{self.__dict__}'

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
        raise

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
    ) -> RequestResponse:
        """requests.delete"""

        url, data, headers = self._params(url, data, headers)
        self._set_retry(max_retries=max_retries)
        self._set_proxy()

        logger.debug(f'[RequestsClient] :: DELETE :: {url=} :: {data=} :: {headers=} :: {self.proxies=} :: {kwargs=}')

        response = self.session.delete(url=url, data=data, headers=headers, proxies=self.proxies, **kwargs)
        return RequestResponse(response)

    def delete_self(self, *args, **kwargs):
        return self.delete(*args, **kwargs)

    def get(
            self,
            url: str = None,
            data: dict = None,
            headers: dict = None,
            max_retries: int = None,
            **kwargs
    ) -> RequestResponse:
        """requests.get"""

        url, data, headers = self._params(url, data, headers)
        self._set_retry(max_retries=max_retries)
        self._set_proxy()

        logger.debug(f'[RequestsClient] :: GET :: {url=} :: {data=} :: {headers=} :: {self.proxies=} :: {kwargs=}')

        response = self.session.get(url=url, data=data, headers=headers, proxies=self.proxies, **kwargs)
        return RequestResponse(response)

    def get_self(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def patch(
            self,
            url: str = None,
            data: dict = None,
            headers: dict = None,
            max_retries: int = None,
            **kwargs,
    ) -> RequestResponse:
        """requests.patch"""

        url, data, headers = self._params(url, data, headers)
        self._set_retry(max_retries=max_retries)
        self._set_proxy()

        logger.debug(f'[RequestsClient] :: PATCH :: {url=} :: {data=} :: {headers=} :: {self.proxies=} :: {kwargs=}')

        response = self.session.patch(url=url, data=data, headers=headers, proxies=self.proxies, **kwargs)
        return RequestResponse(response)

    def patch_self(self, *args, **kwargs):
        return self.patch(*args, **kwargs)

    def post(
            self,
            url: str = None,
            data: any = None,
            headers: dict = None,
            max_retries: int = None,
            **kwargs
    ) -> RequestResponse:
        """requests.post"""

        url, data, headers = self._params(url, data, headers)
        self._set_retry(max_retries=max_retries)
        self._set_proxy()

        logger.debug(f'[RequestsClient] :: POST :: {url=} :: {data=} :: {headers=} :: {self.proxies=} :: {kwargs=}')

        response = self.session.post(url=url, data=data, headers=headers, proxies=self.proxies, **kwargs)
        return RequestResponse(response)

    def post_self(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def put(
            self,
            url: str = None,
            data: dict = None,
            headers: dict = None,
            max_retries: int = None,
            **kwargs
    ) -> RequestResponse:
        """requests.put"""

        url, data, headers = self._params(url, data, headers)
        self._set_retry(max_retries=max_retries)
        self._set_proxy()

        logger.debug(f'[RequestsClient] :: PUT :: {url=} :: {data=} :: {headers=} :: {self.proxies=} :: {kwargs=}')

        response = self.session.put(url=url, data=data, headers=headers, proxies=self.proxies, **kwargs)
        return RequestResponse(response)

    def put_self(self, *args, **kwargs):
        return self.put(*args, **kwargs)

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
