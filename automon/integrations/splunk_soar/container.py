import json
import datetime

from automon.log import Logging

from .datatypes import AbstractDataType

log = Logging('Container', level=Logging.CRITICAL)


class Container(AbstractDataType):
    artifact_count: int
    start_time: datetime
    id: int
    name: str

    def __init__(self, container: dict = {}):
        self.artifact_count = None
        self.start_time = None
        self.id = None
        self.name = None
        self.__dict__.update(container)

    def __repr__(self):
        return self.name
