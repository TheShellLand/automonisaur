import json

from dateutil import parser
from typing import Optional

from .container import Container


class GeneralResponse:
    def __init__(self, results: dict = {}):
        self.__dict__.update(results)

    def __repr__(self):
        return f'{self.__dict__}'


class Response(GeneralResponse):
    count: int
    num_pages: int
    data: list = None


class CreateContainerResponse(GeneralResponse):
    success: bool
    id: int = None
    new_artifacts_ids: list


class RunPlaybookResponse(GeneralResponse):
    playbook_run_id: str = None
    received: bool


class Playbook(GeneralResponse):
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
        return f'{self.playbook_name}'

    def __len__(self):
        return self.playbook

    @property
    def message_to_dict(self):
        return json.loads(self.message)

    @property
    def playbook_name(self):
        return self.message_to_dict['playbook']

    @property
    def start_time_parsed(self):
        return parser.parse(self.start_time)

    @property
    def update_time_parsed(self):
        return parser.parse(self.update_time)
