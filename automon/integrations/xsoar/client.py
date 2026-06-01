import json

from lxml.html.diff import end_tag

from automon.log import logging
from automon.helpers.debug import debug_exception
from automon.helpers.repr import repr_str
from automon.integrations.requestsWrapper import RequestsClient, RequestResponse

from .config import XSOARConfig
from .classes.incident import *
from .classes.indicator import *

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
            verify_certs: bool = False,
    ):
        self.config = config or XSOARConfig(
            host=host,
            api_key=api_key,
            api_key_id=api_key_id,
            xsoar_version=xsoar_version,
            verify_certs=verify_certs,
        )
        self.api = self.config.api

        self._requests = RequestsClient()

        self._incidents_search = {}
        self._file = None

    def is_ready(self):
        if self.config.is_ready():
            return True
        return False

    def auth(self):
        raise NotImplementedError

    def _get(self, endpoint: str) -> RequestResponse:
        url = f'{self.config.host}/{endpoint}'
        logger.debug(f'[XSOARClient] :: get :: {url=}')

        response = self._requests.get(url=url, headers=self.config.headers, verify=self.config.verify_cert)

        if response:
            return response

        raise debug_exception(locals(), 'get failed')

    def _post(
            self,
            endpoint: str,
            params: dict = None,
            data: dict = None,
    ) -> RequestResponse:
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
            return response

        status_code = response.status_code
        if status_code == 201:
            return response

        raise debug_exception(locals(), 'post failed')

    def download_file(self, entryid: str):

        file = self._get(endpoint=self.api.files.get_by_entryid(entryid=entryid))

        if file:
            return file

        raise debug_exception(locals(), 'download_file failed')

    def incident_create(
            self,
            name: str = None,
            type: str = None,
            playbookId: str = None,
            labels: list = [],
            createInvestigation: bool = True,
            body: dict = None
    ) -> Incident:

        if name or type:
            if body:
                raise debug_exception(locals(), '`body` arg must be used by itself')

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
            endpoint=self.api.incidents.create_incident,
            data=incident,
        )

        if incident:
            incident = Incident(incident)
            return incident

        raise debug_exception(locals(), 'failed to create incident')

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
            endpoint=self.api.incidents.delete_incident_batch(),
            data=incident,
        )

        if incident:
            incident['data'] = [Incident(x) for x in incident['data']]
            return incident

        raise debug_exception(locals(), 'failed to delete incident')

    def incidents_search(
            self,
            query: str = None,
            id: int | str = None,
            ids: list = None,
            name: list = None,
            type: list = None,
            body: dict = None,
    ):

        api = self.api.incidents.search_incident

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

        incidents = self._post(endpoint=api, data=incident)

        if incidents:
            incidents['data'] = [Incident(x) for x in incidents.get('data')]
            return incidents

        raise debug_exception(locals(), 'failed to search incidents')

    def playbook_search(self):
        return self

    def reports(self):
        api = self.api.reports.reports
        reports = self._get(endpoint=api)
        logger.debug(f'[XSOARClient] :: reports :: {reports=}')
        return reports
