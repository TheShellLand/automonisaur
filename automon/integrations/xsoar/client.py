import json

from lxml.html.diff import end_tag

from automon.log import logging
from automon.integrations.requestsWrapper import RequestsClient

from .config import XSOARConfig

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
            config: XSOARConfig = None,
            xsoar_version: int = 6,
    ):
        self.config = config or XSOARConfig(
            host=host,
            api_key=api_key,
            api_key_id=api_key_id,
            xsoar_version=xsoar_version
        )
        self.api = self.config.api

        self._requests = RequestsClient()

        self._incident_created = None
        self._incidents = {}
        self._file = None

    def is_ready(self):
        if self.config.is_ready():
            return True
        return False

    def auth(self):
        raise NotImplementedError

    @property
    def _client_errors(self):
        return self._requests.errors

    def _get(self, endpoint: str):
        url = f'{self.config.host}/{endpoint}'
        logger.debug(f'[XSOARClient] :: get :: {url=}')

        response = self._requests.get(url=url, headers=self.config.headers, verify=self.config.verify_cert)

        if response:
            logger.info(f'[XSOARClient] :: get :: done')
            return response

        error = self._client_errors
        logger.error(f'[XSOARClient] :: get :: ERROR :: {error=}')
        raise Exception(self._client_errors)

    def _post(
            self,
            endpoint: str,
            params: dict = None,
            data: dict = None,
    ):
        url = f'{self.config.host}/{endpoint}'
        logger.debug(f'[XSOARClient] :: post :: {url=}')

        data = json.dumps(data)

        response = self._requests.post(
            url=url,
            headers=self.config.headers,
            verify=self.config.verify_cert,
            params=params,
            data=data,
        )

        if response:
            logger.info(f'[XSOARClient] :: post :: done')
            return response

        if self._requests.status_code == 201:
            status_code = self._requests.status_code
            logger.info(f'[XSOARClient] :: post :: {status_code=} :: done')
            return True

        error = self._client_errors
        logger.error(f'[XSOARClient] :: post :: ERROR :: {error=}')
        raise Exception(self._client_errors)

    def create_incident(self, body: dict):

        incident = self._post(
            endpoint=self.api.Incidents().create_incident,
            data=body,
        )

        if incident:
            incident = self._requests.to_dict()
            self._incident_created = incident
            logger.debug(f'[XSOARClient] :: create_incident :: {incident=}')
            print(f'[XSOARClient] :: create_incident :: {incident=}')
            logger.info(f'[XSOARClient] :: create_incident :: done')
            return self

        logger.error(f'[XSOARClient] :: create_incident :: ERROR :: {self._requests.content}')
        raise Exception

    def download_file(self, entryid: str):

        file = self._get(endpoint=self.api.Files().get_by_entryid(entryid=entryid))

        if file:
            file = self._requests.to_dict()
            self._file = file
            logger.debug(f'[XSOARClient] :: download_file :: {file=}')
            logger.info(f'[XSOARClient] :: download_file :: done')
            return self

        logger.error(f'[XSOARClient] :: download_file :: ERROR :: {self._requests.content}')
        raise Exception

    def incidents(
            self,
            id: str = None
    ):

        data = {
            "filter": {
                "id": [
                    id
                ]
            }
        }
        incidents = self._post(endpoint=self.api.Incidents.incidents, data=data)

        if incidents:
            incidents = self._requests.to_dict()
            self._incidents = incidents
            logger.debug(
                f'[XSOARClient] :: incidents'
                f' :: {incidents["total"]} total'
                f' :: {len(incidents["data"])} results')
            logger.info(f'[XSOARClient] :: incidents :: done')
            return self

        logger.error(f'[XSOARClient] :: incidents :: ERROR :: {self._requests.content}')
        raise Exception

    def reports(self):
        reports = self._get(endpoint=self.api.Reports.reports)
        logger.debug(f'[XSOARClient] :: reports :: {reports=}')
        logger.info(f'[XSOARClient] :: reports :: done')
        return reports
