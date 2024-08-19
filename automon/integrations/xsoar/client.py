from automon.log import logging
from automon.integrations.requestsWrapper import RequestsClient

from .config import XSOARConfig
from .endpoints import v1

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)


class XSOARClient(object):
    """XSOAR REST API client

    referenc: https://cortex-panw.stoplight.io/docs/cortex-xsoar-8/kjn2q21a7yrbm-get-started-with-cortex-xsoar-8-ap-is
    """

    def __init__(
            self,
            host: str = None,
            api_key: str = None,
            api_key_id: str = None,
            config: XSOARConfig = None
    ):
        self.config = config or XSOARConfig(host=host, api_key=api_key, api_key_id=api_key_id)
        self._requests = RequestsClient()

    async def is_ready(self):
        if self.config.is_ready():
            return True
        return False

    async def auth(self):
        return

    @property
    def errors(self):
        return self._requests.errors

    async def get(self, endpoint: str):
        logger.info(dict(
            endpoint=f'{self.config.host}/{endpoint}'
        ))
        response = await self._requests.get(url=f'{self.config.host}/{endpoint}', headers=self.config.headers)

        if response:
            return response

        logger.error(self.errors)
        raise Exception(self.errors)

    async def post(self, endpoint: str):
        logger.info(dict(
            endpoint=f'{self.config.host}/{endpoint}'
        ))
        response = self._requests.post(url=f'{self.config.host}/{endpoint}', headers=self.config.headers)

        if response:
            return response

        logger.error(self.errors)
        raise Exception(self.errors)

    async def reports(self):
        reports = await self.get(endpoint=v1.Reports.reports)
        logger.info(dict(
            reports=self._requests.content
        ))
        return reports
