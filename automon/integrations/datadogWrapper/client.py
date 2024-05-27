from automon.integrations.requestsWrapper import RequestsClient
from automon import log

from .config import DatadogConfigRest
from .api import V1, V2

logger = log.logging.getLogger(__name__)
logger.setLevel(log.logging.DEBUG)


class DatadogClientRest(object):

    def __init__(self, host: str = None, api_key: str = None):
        self.config = DatadogConfigRest(host=host, api_key=api_key)
        self.requests = RequestsClient()

    async def is_ready(self):
        if await self.config.is_ready():
            if await self.validate():
                return True
        logger.error(f'client not ready')

    async def log(self, ddsource: str, hostname: str, service: str, message: str, ddtags: str = 'env:test,version:0.1'):
        url = V2(self.config.host_log).api.logs.endpoint

        log = {
            "ddsource": ddsource,
            "ddtags": ddtags,
            "hostname": hostname,
            "service": service,
            'message': message
        }

        logger.debug(log)

        response = await self.requests.post(url=url, json=log)
        response_log = await self.requests.to_dict()

        return response_log

    async def validate(self):
        url = V1(self.config.host).api.validate.endpoint

        self.requests.session.headers.update(await self.config.headers())
        response = await self.requests.get(url=url)
        response_validate = await self.requests.to_dict()

        return response_validate
