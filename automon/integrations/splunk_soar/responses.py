import json

from dateutil import parser
from typing import Optional

from automon.log import Logging

from .container import Container
from .vault import Vault

log = Logging(name='Responses', level=Logging.DEBUG)


class GeneralResponse:
    def __init__(self, results: dict = {}):
        self.__dict__.update(results)

    def __repr__(self):
        return f'{self.__dict__}'


class CancelPlaybookResponse(GeneralResponse):
    cancelled: int = None
    message: str = None
    playbook_run_id: int = None


class CloseContainerResponse(GeneralResponse):
    id: int = None
    success: bool = None


class CreateContainerAttachmentResponse(GeneralResponse):
    succeeded: bool = None
    message: str = None
    hash: str = None
    vault_id: str = None
    container: int = None
    size: int = None
    id: int = None
    created_via: str = None

    @property
    def vault_id(self):
        return self.hash


class CreateContainerResponse(GeneralResponse):
    success: bool
    id: int = None
    new_artifacts_ids: list


class GenericResponse(GeneralResponse):
    count: int
    num_pages: int
    data: list = None


class PlaybookRun(GeneralResponse):
    action_exec: list
    cancelled: Optional[bool]
    container: int = None
    effective_user: int
    id: int = None
    ip_address: str
    last_artifact: int = None
    log_level: int
    message: str = None
    misc: dict = None
    node_guid: Optional[int]
    owner: int = None
    parent_run: Optional[int] = None
    playbook: int = None
    playbook_run_id: Optional[int] = None
    run_data: dict = None
    start_time: str = None
    status: str = None
    test_mode: str = None
    update_time: str = None
    version: int

    def __repr__(self):
        return f'[{self.status}] {self.playbook_name}'

    def __len__(self):
        return self._playbook_run_id

    @property
    def _playbook_run_id(self):
        if self.playbook_run_id:
            return self.playbook_run_id
        return self.id

    @property
    def message_to_dict(self) -> Optional[dict]:
        try:
            return json.loads(self.message)
        except Exception as e:
            log.warn(f'message is not json. {e}')

    @property
    def playbook_name(self):
        if self.message_to_dict:
            return self.message_to_dict['playbook']
        return ''

    @property
    def start_time_parsed(self):
        return parser.parse(self.start_time)

    @property
    def update_time_parsed(self):
        return parser.parse(self.update_time)


class Response(GeneralResponse):
    count: int
    num_pages: int
    data: list = None


class RunPlaybookResponse(GeneralResponse):
    playbook_run_id: str = None
    received: bool


class UpdatePlaybookResponse(GeneralResponse):
    message: int = None
    success: bool = None


class VaultResponse(GeneralResponse):
    count: int = None
    data: list = None
    num_pages: int = None

    def __repr__(self):
        return f'{dict(count=self.count, num_pages=self.num_pages)}'

    @property
    def data_parsed(self):
        return [Vault(x) for x in self.data]

    def get_one(self):
        if self.data_parsed:
            return self.data_parsed[-1]
