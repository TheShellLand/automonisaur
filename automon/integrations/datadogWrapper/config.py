from automon import environ


class DatadogConfigRest(object):
    api_key: str

    def __init__(self, host: str = 'https://api.datadoghq.com', api_key: str = None):
        self.host = host or environ('DD_SITE')
        self.api_key = api_key or environ('DD_API_KEY')

    async def is_ready(self):
        if self.host and self.api_key:
            return True

    async def headers(self):
        if await self.is_ready():
            return {
                'DD-API-KEY': f'{self.api_key}',
                'Accept': 'application/json',
            }
