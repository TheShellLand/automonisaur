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
        self._incident_deleted = None
        self._incidents_search = {}
        self._file = None

    def is_ready(self):
        if self.config.is_ready():
            return True
        return False

    def auth(self):
        raise NotImplementedError

    @property
    def _client_content(self):
        return self._requests.content

    @property
    def _client_errors(self):
        return self._requests.errors

    @property
    def _client_response(self):
        return self._requests.to_dict()

    def _get(self, endpoint: str):
        url = f'{self.config.host}/{endpoint}'
        logger.debug(f'[XSOARClient] :: get :: {url=}')

        response = self._requests.get(url=url, headers=self.config.headers, verify=self.config.verify_cert)

        if response:
            logger.info(f'[XSOARClient] :: get :: done')
            return response

        error = self._client_errors
        logger.error(f'[XSOARClient] :: get :: ERROR :: {error=}')
        raise Exception(f'[XSOARClient] :: get :: ERROR :: {error=}')

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
        raise Exception(f'[XSOARClient] :: post :: ERROR :: {error=}')

    def download_file(self, entryid: str):

        file = self._get(endpoint=self.api.Files().get_by_entryid(entryid=entryid))

        if file:
            file = self._client_response
            self._file = file
            logger.debug(f'[XSOARClient] :: download_file :: {file=}')
            logger.info(f'[XSOARClient] :: download_file :: done')
            return self

        logger.error(f'[XSOARClient] :: download_file :: ERROR :: {self._client_content}')
        raise Exception

    def incident_create(self,
                        name: str = None,
                        type: str = None,
                        labels: list = [],
                        createInvestigation: bool = True,

                        body: dict = None
                        ):

        if name or type:
            if body:
                raise Exception(f'[XSOARClient] :: incident_create :: ERROR :: `body` must be used by itself')

        incident = {}

        if name:
            incident['name'] = name

        if type:
            incident['type'] = type

        if not name and not type:
            incident['name'] = 'Test'

        if labels:
            incident['labels'] = labels

        if createInvestigation:
            incident['createInvestigation'] = createInvestigation

        incident = self._post(
            endpoint=self.api.Incidents().create_incident,
            data=incident,
        )

        if incident:
            incident = self._client_response
            self._incident_created = incident
            logger.debug(f'[XSOARClient] :: incident_create :: {incident=}')
            print(f'[XSOARClient] :: incident_create :: {incident=}')
            logger.info(f'[XSOARClient] :: incident_create :: done')
            return self

        logger.error(f'[XSOARClient] :: incident_create :: ERROR :: {self._client_content}')
        raise Exception

    def incident_delete(self, body: dict):

        incident = self._post(
            endpoint=self.api.Incidents().delete_incident_batch(),
            data=body,
        )

        if incident:
            incident = self._client_response
            self._incident_deleted = incident
            logger.debug(f'[XSOARClient] :: incident_delete :: {incident=}')
            print(f'[XSOARClient] :: incident_delete :: {incident=}')
            logger.info(f'[XSOARClient] :: incident_delete :: done')
            return self

        logger.error(f'[XSOARClient] :: incident_delete :: ERROR :: {self._client_content}')
        raise Exception

    def incidents_search(
            self,
            id: str = None
    ):

        data = {}

        data['filter'] = {}

        if id:
            data['filter']['id'] = [id]

        incidents = self._post(endpoint=self.api.Incidents.incidents, data=data)

        if incidents:
            incidents = self._client_response
            self._incidents_search = incidents
            logger.debug(
                f'[XSOARClient] :: incidents'
                f' :: {incidents["total"]} total'
                f' :: {len(incidents["data"])} results')
            logger.info(f'[XSOARClient] :: incidents :: done')
            return self

        logger.error(f'[XSOARClient] :: incidents :: ERROR :: {self._client_content}')
        raise Exception

    def reports(self):
        reports = self._get(endpoint=self.api.Reports.reports)
        logger.debug(f'[XSOARClient] :: reports :: {reports=}')
        logger.info(f'[XSOARClient] :: reports :: done')
        return reports
