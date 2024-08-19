from .client import RequestsClient
from .config import RequestsConfig

from automon import log

logger = log.logging.getLogger(__name__)
logger.setLevel(log.DEBUG)


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

    async def get(self, url: str, data: str = None, headers: dict = None) -> bool:
        return await self.requests.get(url=url, data=data, headers=headers)

    async def post(self, url: str, data: str = None, headers: dict = None) -> bool:
        return await self.requests.post(url=url, data=data, headers=headers)

    async def delete(self, url: str, data: str = None, headers: dict = None) -> bool:
        return await self.requests.delete(url=url, data=data, headers=headers)

    async def patch(self, url: str, data: str = None, headers: dict = None) -> bool:
        return await self.requests.patch(url=url, data=data, headers=headers)

    def __repr__(self):
        return f'{self.__dict__}'
