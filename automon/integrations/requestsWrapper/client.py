import json
import requests

from automon.log import Logging
from .config import RequestsConfig

log = Logging(name='RequestsClient', level=Logging.DEBUG)


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

    def _log_result(self):
        if self.results.status_code == 200:
            msg = f'{self.results.status_code} ' \
                  f'{self.results.request.method} ' \
                  f'{self.results.url} ' \
                  f'{round(len(self.results.content) / 1024, 2)} KB'
            return log.debug(msg)

        msg = f'{self.results.status_code} ' \
              f'{self.results.request.method} ' \
              f'{self.results.url} ' \
              f'{round(len(self.results.content) / 1024, 2)} KB ' \
              f'{self.results.content}'
        return log.error(msg, raise_exception=False)

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
        if self.results is not None:
            return self.results.content

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
            log.error(f'delete failed. {e}', enable_traceback=False)
        return False

    def get(self,
            url: str = None,
            data: dict = None,
            headers: dict = None, **kwargs) -> bool:
        """requests.get"""

        url, data, headers = self._params(url, data, headers)

        try:
            self.results = requests.get(url=url, data=data, headers=headers, **kwargs)
            self._log_result()
            return True
        except Exception as e:
            self.errors = e
            log.error(f'get failed. {e}', enable_traceback=False)
        return False

    def patch(self,
              url: str = None,
              data: dict = None,
              headers: dict = None, **kwargs) -> bool:
        """requests.patch"""

        url, data, headers = self._params(url, data, headers)

        try:
            self.results = requests.patch(url=url, data=data, headers=headers, **kwargs)
            self._log_result()
            return True
        except Exception as e:
            self.errors = e
            log.error(f'patch failed. {e}', enable_traceback=False)
        return False

    def post(self,
             url: str = None,
             data: dict = None,
             headers: dict = None, **kwargs) -> bool:
        """requests.post"""

        url, data, headers = self._params(url, data, headers)

        try:
            self.results = requests.post(url=url, data=data, headers=headers, **kwargs)
            self._log_result()
            return True
        except Exception as e:
            self.errors = e
            log.error(f'post failed. {e}', enable_traceback=False)
        return False

    def put(self,
            url: str = None,
            data: dict = None,
            headers: dict = None, **kwargs) -> bool:
        """requests.put"""

        url, data, headers = self._params(url, data, headers)

        try:
            self.results = requests.put(url=url, data=data, headers=headers, **kwargs)
            self._log_result()
            return True
        except Exception as e:
            self.errors = e
            log.error(f'put failed. {e}', enable_traceback=False)
        return False

    def to_dict(self):
        if self.results is not None:
            return json.loads(self.results.content)


class Requests(RequestsClient):
    pass
