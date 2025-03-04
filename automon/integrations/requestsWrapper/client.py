import json
import requests

from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO
from .config import RequestsConfig

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


class RequestsClient(object):
    def __init__(self, url: str = None, data: dict = None, headers: dict = None,
                 config: RequestsConfig = None):
        """Wrapper for requests library"""

        self.config = config or RequestsConfig()

        self.url: str = url
        self.data: dict = data
        self.errors: bytes = b''
        self.headers: dict = headers
        self.response = None
        self.requests = requests
        self.session = self.requests.Session()
        self.proxies = self.config.get_proxy()

    def __repr__(self):
        return f'{self.__dict__}'

    def __len__(self):
        if self.content:
            len(self.content)

    def _log_result(self):
        if self.status_code == 200:
            msg = [
                'RequestsClient',
                self.response.request.method,
                f'{self.status_code}',
                f'{self.response.url}',
                f'{self.proxies=}',
                f'{round(len(self.content) / 1024, 2)} KB',
            ]
            msg = ' :: '.join([str(x) for x in msg])
            return logger.debug(msg)

        msg = [
            'RequestsClient',
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
        if 'content' in dir(self.response):
            return self.response.content

    def content_to_dict(self):
        return self.to_dict()

    def delete(
            self,
            url: str = None,
            data: dict = None,
            headers: dict = None,
            **kwargs
    ) -> bool:
        """requests.delete"""

        url, data, headers = self._params(url, data, headers)

        self._set_proxy()

        logger.debug(f'RequestsClient :: DELETE :: {url=} :: {data=} :: {headers=} :: {self.proxies=} :: {kwargs=}')

        try:
            self.response = self.session.delete(url=url, data=data, headers=headers, proxies=self.proxies, **kwargs)
            self._log_result()

            if self.status_code == 200:
                return True

            return False
        except Exception as error:
            self.errors = error
            raise Exception(f'RequestsClient :: DELETE :: ERROR :: {error=}')
        return False

    def _set_proxy(self):
        if self.config.proxies:
            if self.config.use_random_proxies:
                self.proxies = self.config.get_random_proxy()
            else:
                self.proxies = self.config.get_proxy()

        logger.debug(f'RequestsClient :: SET PROXY :: {self.proxies}')

    def get(
            self,
            url: str = None,
            data: dict = None,
            headers: dict = None,
            **kwargs
    ) -> bool:
        """requests.get"""

        url, data, headers = self._params(url, data, headers)

        self._set_proxy()

        logger.debug(f'RequestsClient :: GET :: {url=} :: {data=} :: {headers=} :: {self.proxies=} :: {kwargs=}')

        try:
            self.response = self.session.get(url=url, data=data, headers=headers, proxies=self.proxies, **kwargs)
            self._log_result()

            if self.status_code == 200:
                return True

            self.errors = self.content

            return False
        except Exception as error:
            self.errors = error
            raise Exception(f'RequestsClient :: GET :: ERROR :: {error=}')
        return False

    def patch(
            self,
            url: str = None,
            data: dict = None,
            headers: dict = None,
            **kwargs
    ) -> bool:
        """requests.patch"""

        url, data, headers = self._params(url, data, headers)

        self._set_proxy()

        logger.debug(f'RequestsClient :: PATCH :: {url=} :: {data=} :: {headers=} :: {self.proxies=} :: {kwargs=}')

        try:
            self.response = self.session.patch(url=url, data=data, headers=headers, proxies=self.proxies, **kwargs)
            self._log_result()

            if self.status_code == 200:
                return True

            self.errors = self.content

            return False
        except Exception as error:
            self.errors = error
            raise Exception(f'RequestsClient :: PATCH :: ERROR :: {error=}')
        return False

    def post(
            self,
            url: str = None,
            data: dict = None,
            headers: dict = None,
            **kwargs
    ) -> bool:
        """requests.post"""

        url, data, headers = self._params(url, data, headers)

        self._set_proxy()

        logger.debug(f'RequestsClient :: POST :: {url=} :: {data=} :: {headers=} :: {self.proxies=} :: {kwargs=}')

        try:
            self.response = self.session.post(url=url, data=data, headers=headers, proxies=self.proxies, **kwargs)
            self._log_result()

            if self.status_code == 200:
                return True

            self.errors = self.content

            return False
        except Exception as error:
            self.errors = error
            raise Exception(f'RequestsClient :: POST :: ERROR :: {error=}')
        return False

    def put(
            self,
            url: str = None,
            data: dict = None,
            headers: dict = None,
            **kwargs
    ) -> bool:
        """requests.put"""

        url, data, headers = self._params(url, data, headers)

        self._set_proxy()

        logger.debug(f'RequestsClient :: PUT :: {url=} :: {data=} :: {headers=} :: {self.proxies=} :: {kwargs=}')

        try:
            self.response = self.session.put(url=url, data=data, headers=headers, proxies=self.proxies, **kwargs)
            self._log_result()

            if self.status_code == 200:
                return True

            self.errors = self.content

            return False
        except Exception as error:
            self.errors = error
            raise Exception(f'RequestsClient :: PUT :: ERROR :: {error=}')
        return False

    @property
    def reason(self):
        if 'reason' in dir(self.response):
            return self.response.reason

    @property
    def status_code(self):
        if 'status_code' in dir(self.response):
            return self.response.status_code

    @property
    def text(self):
        if self.response:
            return self.response.text

    def to_dict(self):
        if self.response is not None:
            try:
                return json.loads(self.content)
            except Exception as error:
                logger.error(f'RequestsClient :: TO DICT :: ERROR :: {error=}')

    def to_json(self):
        if self.content:
            try:
                return json.dumps(json.loads(self.content))
            except Exception as error:
                logger.error(f'RequestsClient :: TO JSON :: ERROR :: {error=}')

    def update_headers(self, headers: dict):
        return self.session.headers.update(headers)


class Requests(RequestsClient):
    pass
