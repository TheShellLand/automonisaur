from automon import environ
from automon import log

logger = log.logging.getLogger(__name__)
logger.setLevel(log.logging.DEBUG)


class DatadogConfigRest(object):
    api_key: str

    def __init__(self, host: str = 'https://api.datadoghq.com', api_key: str = None, app_key: str = None):
        self.host = host or environ('DD_SITE')
        self.host_log = 'https://http-intake.logs.us5.datadoghq.com'
        self.api_key = api_key or environ('DD_API_KEY')
        self.app_key = app_key or environ('DD_APP_KEY')

    async def is_ready(self):
        if self.host and self.api_key and self.app_key:
            return True
        logger.error(f'missing DD_SITE DD_API_KEY DD_APP_KEY')

    async def headers(self):
        if await self.is_ready():
            return {
                'DD-API-KEY': f'{self.api_key}',
                'DD-APPLICATION-KEY': f'{self.app_key}',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            }
