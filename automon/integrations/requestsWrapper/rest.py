from .client import RequestsClient
from .config import RequestsConfig

from automon.log import logger

log = logger.logging.getLogger(__name__)
log.setLevel(logger.DEBUG)

class BaseRestClient:
    requests: RequestsClient
    config: RequestsConfig

    def __init__(self, config: RequestsConfig = None):
        """Base REST Client"""
        self.config = config or RequestsConfig()
        self.requests = RequestsClient()

    def isConnected(self):
        if self.config.is_ready:
            return True
        return False

    def get(self, url: str, data: str = None, headers: dict = None) -> bool:
        return self.requests.get(url=url, data=data, headers=headers)

    def post(self, url: str, data: str = None, headers: dict = None) -> bool:
        return self.requests.post(url=url, data=data, headers=headers)

    def delete(self, url: str, data: str = None, headers: dict = None) -> bool:
        return self.requests.delete(url=url, data=data, headers=headers)

    def patch(self, url: str, data: str = None, headers: dict = None) -> bool:
        return self.requests.patch(url=url, data=data, headers=headers)

    def __repr__(self):
        return f'{self.__dict__}'
