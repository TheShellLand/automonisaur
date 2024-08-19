import os

from automon import log

logger = log.logging.getLogger(__name__)
logger.setLevel(log.ERROR)


class ShodanConfig:
    token = os.getenv('SHODAN_API')

    def __init__(self):
        self.token = os.getenv('SHODAN_API')

        if not self.token:
            logger.error(f'Missing SHODAN_API')


class Shodan:
    """Get any Shodan information"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key if api_key else ShodanConfig.token

    # TODO: add shodan geoip
    def request(self):
        pass
