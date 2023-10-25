import json
import requests

from automon.log import logger
from .config import RequestsConfig

log = logger.logging.getLogger(__name__)
log.setLevel(logger.DEBUG)


class RequestsClient(object):
    def __init__(self, url: str = None, data: dict = None, headers: dict = None,
                 config: RequestsConfig = None):
        """Wrapper for requests library"""

        self.config = config or RequestsConfig()

        self.url = url
        self.data = data
        self.errors = None
        self.headers = headers
        self.results = None
        self.requests = requests

        if url:
            self.url = url
            self.get(url=self.url, data=self.data, headers=self.headers)

    def __repr__(self):
        return f'{self.__dict__}'

    def __len__(self):
        if self.content:
            len(self.content)

    def _log_result(self):
        if self.results.status_code == 200:
            msg = [
                self.results.request.method,
                self.results.url,
                f'{round(len(self.results.content) / 1024, 2)} KB',
                self.results.status_code,
            ]
            msg = ' '.join(msg)
            return log.debug(msg)

        msg = [
            self.results.request.method,
            self.results.url,
            f'{round(len(self.results.content) / 1024, 2)} KB',
            self.results.status_code,
            self.results.content
        ]

        msg = ' '.join(msg)
        return log.error(msg)

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
        if self.results:
            return self.results.content

    @property
    def text(self):
        if self.results:
            return self.results.text

    def delete(self,
               url: str = None,
               data: dict = None,
               headers: dict = None, **kwargs) -> bool:
        """requests.delete"""

        url, data, headers = self._params(url, data, headers)

        try:
            self.results = requests.delete(url=url, data=data, headers=headers, **kwargs)
            self._log_result()
            return True
        except Exception as e:
            self.errors = e
            log.error(f'delete failed. {e}')
        return False

    def get(self,
            url: str = None,
            data: dict = None,
            headers: dict = None, **kwargs) -> bool:
        """requests.get"""

        url, data, headers = self._params(url, data, headers)

        try:
            self.results = requests.get(url=url, data=data, headers=headers, **kwargs)

            log.debug(
                f'{self.results.url} '
                f'{round(len(self.results.content) / 1024, 2)} KB '
                f'{self.results.status_code}'
            )

            return True
        except Exception as e:
            self.errors = e
            log.error(f'{e}')
        return False

    def patch(self,
              url: str = None,
              data: dict = None,
              headers: dict = None, **kwargs) -> bool:
        """requests.patch"""

        url, data, headers = self._params(url, data, headers)

        try:
            self.results = requests.patch(url=url, data=data, headers=headers, **kwargs)

            log.debug(
                f'{self.results.url} '
                f'{round(len(self.results.content) / 1024, 2)} KB '
                f'{self.results.status_code}'
            )

            return True
        except Exception as e:
            self.errors = e
            log.error(f'patch failed. {e}')
        return False

    def post(self,
             url: str = None,
             data: dict = None,
             headers: dict = None, **kwargs) -> bool:
        """requests.post"""

        url, data, headers = self._params(url, data, headers)

        try:
            self.results = requests.post(url=url, data=data, headers=headers, **kwargs)

            log.debug(
                f'{self.results.url} '
                f'{round(len(self.results.content) / 1024, 2)} KB '
                f'{self.results.status_code}'
            )

            return True
        except Exception as e:
            self.errors = e
            log.error(f'post failed. {e}')
        return False

    def put(self,
            url: str = None,
            data: dict = None,
            headers: dict = None, **kwargs) -> bool:
        """requests.put"""

        url, data, headers = self._params(url, data, headers)

        try:
            self.results = requests.put(url=url, data=data, headers=headers, **kwargs)

            log.debug(
                f'{self.results.url} '
                f'{round(len(self.results.content) / 1024, 2)} KB '
                f'{self.results.status_code}'
            )

            return True
        except Exception as e:
            self.errors = e
            log.error(f'put failed. {e}')
        return False

    def to_dict(self):
        if self.results is not None:
            return json.loads(self.results.content)


class Requests(RequestsClient):
    pass
