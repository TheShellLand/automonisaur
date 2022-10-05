import datetime

from automon.log import Logging

from .datatypes import AbstractDataType

log = Logging('Container', level=Logging.CRITICAL)


class Container(AbstractDataType):
    artifact_count: int = None
    start_time: datetime = None
    id: int = None
    name: str = None

    def __repr__(self):
        if self.name:
            return f'{self.name}'
        return f'{self.id}'
