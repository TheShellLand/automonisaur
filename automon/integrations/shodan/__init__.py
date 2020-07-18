import os

from automon.log.logger import Logging

log = Logging(__name__, Logging.ERROR)


class ShodanConfig:
    token = os.getenv('SHODAN_API')

    def __init__(self):
        self._log = Logging(ShodanConfig.__name__, Logging.ERROR)
        self.token = os.getenv('SHODAN_API')

        if not self.token:
            self._log.error(f'Missing SHODAN_API')


class Shodan:
    """Get any Shodan information"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key if api_key else ShodanConfig.token

    # TODO: add shodan geoip
    def request(self):
        pass
