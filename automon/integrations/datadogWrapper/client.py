from automon.integrations.requestsWrapper import RequestsClient
from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO

from .config import DatadogConfigRest
from .api import V1, V2

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


class DatadogClientRest(object):

    def __init__(self, host: str = None, api_key: str = None):
        self.config = DatadogConfigRest(host=host, api_key=api_key)
        self.requests = RequestsClient()

    def is_ready(self):
        if self.config.is_ready():
            if self.validate():
                return True
        logger.error(f'client not ready')

    def log(self, ddsource: str, hostname: str, service: str, message: str, ddtags: str = 'env:test,version:0.1'):
        url = V2(self.config.host_log).api.logs.endpoint

        log = {
            "ddsource": ddsource,
            "ddtags": ddtags,
            "hostname": hostname,
            "service": service,
            'message': message
        }

        logger.debug(log)

        response = self.requests.post(url=url, json=log)
        response_log = self.requests.to_dict()

        return response_log

    def validate(self):
        url = V1(self.config.host).api.validate.endpoint

        self.requests.session.headers.update(self.config.headers())
        response = self.requests.get(url=url)
        response_validate = self.requests.to_dict()

        return response_validate
