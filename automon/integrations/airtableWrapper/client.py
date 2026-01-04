import datetime
import time

from automon.helpers.threadingWrapper import *
from automon.integrations.requestsWrapper import RequestsClient
from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO

from .api import *
from .config import AirtableConfig

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


class AirtableClient(object):
    _global_rate_per_second: int = 5
    _global_rate_per_second_lock: threading.Lock = threading.Lock()

    _global_rate: float = 1 / _global_rate_per_second
    _global_rate_lock: threading.Lock = threading.Lock()

    _last_request_time: float = 0
    _last_request_time_lock: threading.Lock = threading.Lock()

    _api = AirtableApi()

    def __init__(self, config: AirtableConfig = None):
        self.config = config or AirtableConfig()
        self.requests = RequestsClient()
        self.requests_queue = queue.Queue()

        self.requests.set_global_retry(max_retries=1)

    def is_ready(self):
        if self.config.is_ready():
            self.requests.headers = self.config.headers()
            return True
        return False

    def _wait_for_rate_limit(self):
        while self._is_rate_limited():
            time.sleep(0.2)

    def _is_rate_limited(self):
        with AirtableClient._global_rate_lock:
            max_rate = AirtableClient._global_rate

        with AirtableClient._last_request_time_lock:
            if AirtableClient._last_request_time:
                time_since_last_request = time.time() - AirtableClient._last_request_time
            else:
                time_since_last_request = 0

        if time_since_last_request and max_rate > time_since_last_request:
            logger.debug(f'[AirtableClient] :: _is_rate_limited :: True :: {time_since_last_request=}')
            return True

        logger.debug(f'[AirtableClient] :: _is_rate_limited :: False :: {time_since_last_request=}')
        return False

    def _update_last_request(self):
        with AirtableClient._last_request_time_lock:
            AirtableClient._last_request_time = time.time()

    def _requests_get(
            self,
            url: str,
            **kwargs) -> RequestsClient:

        response = self.requests.get_self(url=url, **kwargs)
        self._update_last_request()
        return response

    def _requests_delete(
            self,
            url: str,
            data: dict,
            **kwargs) -> RequestsClient:

        response = self.requests.delete_self(url=url, data=data, **kwargs)
        self._update_last_request()
        return response

    def _requests_post(
            self,
            url: str,
            data: dict,
            **kwargs) -> RequestsClient:

        response = self.requests.post_self(url=url, data=data, **kwargs)
        self._update_last_request()
        return response

    def user_info(self) -> dict:
        self._wait_for_rate_limit()

        url = self._api.users.info()
        response = self._requests_get(url=url).to_dict()

        logger.debug(f'[AirtableClient] :: user_info :: {response=}')
        return response

    def bases_list(self) -> BasesResponse:
        self._wait_for_rate_limit()

        url = self._api.bases.list()
        response = self._requests_get(url=url).to_dict()
        response = BasesResponse().automon_update(response)

        logger.debug(f'[AirtableClient] :: bases_list :: {response=}')
        return response

    def bases_get(self, base_name: str) -> Base | None:
        self._wait_for_rate_limit()
        return self.bases_list().get_base(base_name=base_name)

    def tables_list(self, baseId: str) -> TablesResponse:
        self._wait_for_rate_limit()

        url = self._api.tables.list(baseId=baseId)
        response = self._requests_get(url=url).to_dict()
        response = TablesResponse().automon_update(response)

        logger.debug(f'[AirtableClient] :: tables_list :: {response=}')
        return response

    def tables_create(
            self,
            baseId: str,
            name: str,
            fields: list[TableField],
            description: str = None) -> Table:

        table = Table()
        table.name = name
        table.description = description
        table.fields = fields

        data = table.to_json()
        url = self._api.tables.create(baseId=baseId)
        response = self._requests_post(url=url, data=data).to_dict()
        response = Table().automon_update(response)

        logger.debug(f'[AirtableClient] :: tables_create :: {response=}')
        return response
