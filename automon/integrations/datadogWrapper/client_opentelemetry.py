from automon.log import logging

from .config_opentelemetry import DatadogOpenTelemetryConfig

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class DatadogOpenTelemetryClient(object):

    def __init__(self, host: str = None, api_key: str = None, app_key: str = None):
        self.config = DatadogOpenTelemetryConfig(host=host, api_key=api_key, app_key=app_key)

    async def is_ready(self):
        if await self.config.is_ready():
            return True
        logger.error(f'client not ready')
