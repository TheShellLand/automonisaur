import requests

from automon.log import Logging
from .config import RequestsConfig


class RequestsClient(object):
    def __init__(self, url: str = None, data: dict = None, headers: dict = None,
                 config: RequestsConfig = None):
        """Wrapper for requests library"""

        self._log = Logging(name=RequestsClient.__name__, level=Logging.DEBUG)

        self.config = config or RequestsConfig()

        self.url = url
        self.data = data
        self.headers = headers
        self.results = None
        self.requests = requests

        if url:
            self.url = url
            self.get(url=self.url, data=self.data, headers=self.headers)

    def delete(self,
               url: str = None,
               data: dict = None,
               headers: dict = None, **kwargs) -> bool:
        """requests.delete"""

        try:
            self.results = requests.delete(url=url, data=data, headers=headers, **kwargs)
            self._log.debug(self._log_result())
            return True
        except Exception as e:
            self._log.error(f'delete failed. {e}', enable_traceback=False)
        return False

    def get(self,
            url: str = None,
            data: dict = None,
            headers: dict = None, **kwargs) -> bool:
        """requests.get"""

        try:
            self.results = requests.get(url=url, data=data, headers=headers, **kwargs)
            self._log.debug(self._log_result())
            return True
        except Exception as e:
            self._log.error(f'get failed. {e}', enable_traceback=False)
        return False

    def patch(self,
              url: str = None,
              data: dict = None,
              headers: dict = None, **kwargs) -> bool:
        """requests.patch"""

        try:
            self.results = requests.patch(url=url, data=data, headers=headers, **kwargs)
            self._log.debug(self._log_result())
            return True
        except Exception as e:
            self._log.error(f'patch failed. {e}', enable_traceback=False)
        return False

    def post(self,
             url: str = None,
             data: dict = None,
             headers: dict = None, **kwargs) -> bool:
        """requests.post"""

        try:
            self.results = requests.post(url=url, data=data, headers=headers, **kwargs)
            self._log.debug(self._log_result())
            return True
        except Exception as e:
            self._log.error(f'post failed. {e}', enable_traceback=False)
        return False

    def put(self,
            url: str = None,
            data: dict = None,
            headers: dict = None, **kwargs) -> bool:
        """requests.put"""

        try:
            self.results = requests.put(url=url, data=data, headers=headers, **kwargs)
            self._log.debug(self._log_result())
            return True
        except Exception as e:
            self._log.error(f'put failed. {e}', enable_traceback=False)
        return False

    def _log_result(self):
        return f'{self.results.status_code} ' \
               f'{self.results.url} ' \
               f'{round(len(self.results.content) / 1024, 2)} KB'


class Requests(RequestsClient):
    pass
