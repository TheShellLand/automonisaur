import json

from lxml.html.diff import end_tag

from automon.log import logging
from automon.integrations.requestsWrapper import RequestsClient

from .config import XSOARConfig
from .endpoints import *

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

        status_code = self._requests.status_code
        if status_code == 201:
            logger.info(f'[XSOARClient] :: post :: {status_code=} :: done')
            return True

        error = self._client_errors
        import traceback
        traceback.print_exc()
        raise Exception(f'[XSOARClient] :: post :: ERROR :: {status_code=} :: {error=}')

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

    def incident_create(
            self,
            name: str = None,
            type: str = None,
            playbookId: str = None,
            labels: list = [],
            createInvestigation: bool = True,

            body: dict = None
    ):

        if name or type:
            if body:
                raise Exception(f'[XSOARClient] :: incident_create :: ERROR :: `body` arg must be used by itself')

        incident = {}

        if name:
            incident['name'] = name

        if type:
            incident['type'] = type

        if not name and not type:
            incident['name'] = 'Test'

        if playbookId:
            incident['playbookId'] = playbookId

        if labels:
            incident['labels'] = labels

        if createInvestigation:
            incident['createInvestigation'] = createInvestigation

        if body:
            incident = body

        incident = self._post(
            endpoint=self.api.Incidents().create_incident,
            data=incident,
        )

        if incident:
            incident = self._client_response
            incident = Incident().update(incident)
            self._incident_created = incident
            logger.debug(f'[XSOARClient] :: incident_create :: {incident=}')
            print(f'[XSOARClient] :: incident_create :: {incident=}')
            logger.info(f'[XSOARClient] :: incident_create :: done')
            return self

        logger.error(f'[XSOARClient] :: incident_create :: ERROR :: {self._client_content}')
        raise Exception

    def incident_delete(self, id: str = None, ids: list = None, body: dict = None):

        if id or ids:
            if body:
                raise Exception()

        incident = {}
        incident['filter'] = {}

        if id:
            incident['filter']['ids'] = [id]

        if ids:
            incident['filter']['ids'] = ids

        if body:
            incident = body

        incident = self._post(
            endpoint=self.api.Incidents().delete_incident_batch(),
            data=incident,
        )

        if incident:
            incident = self._client_response
            incident['data'] = [Incident().update(x) for x in incident['data']]
            self._incident_deleted = incident
            logger.debug(f'[XSOARClient] :: incident_delete :: deleted {id=} {ids=}')
            print(f'[XSOARClient] :: incident_delete :: deleted {id=} {ids=}')
            logger.info(f'[XSOARClient] :: incident_delete :: done')
            return self

        logger.error(f'[XSOARClient] :: incident_delete :: ERROR :: {self._client_content}')
        raise Exception

    def incidents_search(
            self,
            query: str = None,
            id: int or str = None,
            ids: list = None,
            name: list = None,
            type: list = None,
            body: dict = None,
    ):

        if query or id or ids or name or type:
            if body:
                raise Exception(f'[XSOARClient] :: incidents :: ERROR :: `body` arg must be used by itself')

        incident = {}

        incident['filter'] = {}

        if query:
            incident['filter']['query'] = query

        if id:
            assert type(id) is str or int, f'[XSOARClient] :: incidents_search :: ERROR :: id is not str or int'
            incident['filter']['id'] = [str(id)]

        if ids:
            incident['filter']['id'] = [str(x) for x in ids]

        if name:
            incident['filter']['name'] = name

        if type:
            incident['filter']['type'] = type

        if body:
            incident = body

        incidents = self._post(endpoint=self.api.Incidents().search_incident, data=incident)

        if incidents:
            incidents = self._client_response
            incidents['data'] = [Incident().update(x) for x in incidents['data']]
            self._incidents_search = incidents
            logger.debug(
                f'[XSOARClient] :: incidents'
                f' :: {incidents["total"]} total'
                f' :: {len(incidents["data"])} results')
            print(
                f'[XSOARClient] :: incidents'
                f' :: {incidents["total"]} total'
                f' :: {len(incidents["data"])} results')
            logger.info(f'[XSOARClient] :: incidents :: done')
            return self

        logger.error(f'[XSOARClient] :: incidents :: ERROR :: {self._client_content}')
        raise Exception(f'[XSOARClient] :: incidents :: ERROR :: {self._client_content}')

    def playbook_search(self):
        return self

    def reports(self):
        reports = self._get(endpoint=self.api.Reports.reports)
        logger.debug(f'[XSOARClient] :: reports :: {reports=}')
        logger.info(f'[XSOARClient] :: reports :: done')
        return reports
