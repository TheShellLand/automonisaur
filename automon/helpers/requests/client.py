import requests

from automon import Logging
from automon.helpers.requests.config import RequestsConfig


class RequestsClient(object):
    def __init__(self, url: str = None, data: dict = None, headers: dict = None,
                 config: RequestsConfig = None):
        self._log = Logging(name=RequestsClient.__name__, level=Logging.DEBUG)

        self.config = config or RequestsConfig()

        self.url = url
        self.data = data
        self.headers = headers
        self.results = None
        self.requests = requests

        if url:
            self.url = url
            self.results = self.get(url=self.url, data=self.data, headers=self.headers)

    def get(self,
            url: str = None,
            data: dict = None,
            headers: dict = None, **kwargs) -> bool:
        try:
            self.results = requests.get(url=url, data=data, headers=headers, **kwargs)
            self._log.debug(f'{self.results.status_code} '
                            f'{self.results.url} '
                            f'{round(len(self.results.content) / 1024, 2)}  KB')
            return True
        except Exception as e:
            self._log.error(f'{self.results.status_code} get failed. {e}', raise_exception=False)
        return False

    def post(self,
             url: str = None,
             data: dict = None,
             headers: dict = None, **kwargs) -> bool:
        try:
            self.results = requests.post(url=url, data=data, headers=headers, **kwargs)
            self._log.debug(f'{self.results.status_code} '
                            f'{self.results.url} '
                            f'{round(len(self.results.content) / 1024, 2)}  KB')
            return True
        except Exception as e:
            self._log.error(f'{self.results.status_code} post failed. {e}', raise_exception=False)
        return False
