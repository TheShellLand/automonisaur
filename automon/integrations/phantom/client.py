import json

from automon import Logging
from automon.integrations.requests import Requests

from .config import PhantomConfig
from .rest import Urls

log = Logging(name='PhantomClient', level=Logging.DEBUG)


class PhantomClient:
    def __init__(self, host: str = None,
                 user: str = None,
                 password: str = None,
                 config: PhantomConfig = None):
        """Phantom Client"""

        self.config = config or PhantomConfig(host=host, user=user, password=password)
        self.client = Requests(headers=self.config.headers)

    def __repr__(self):
        return f'{self.__dict__}'

    def _content(self):
        return self.client.results.content

    def _get(self, url: str):
        self.client.get(url=url, headers=self.client.headers)
        return self._content()

    def _post(self, url: str, data: dict):
        self.client.post(url=url, headers=self.client.headers, data=data)
        return self._content()

    def isConnected(self):
        self._get(Urls.CONTAINER)

        if self.client.results.status_code == 200:
            log.info(f'Phantom client connected. '
                     f'[{self.client.results.status_code}] '
                     f'{self.config.host}')
            return True

        log.error(f'Phantom client failed. '
                  f'[{self.client.results.status_code}] '
                  f'{self.client.results.text}')
        return False

    def list_containers(self):
        containers = self._get(Urls().container())
        containers = json.loads(containers)

        return containers
