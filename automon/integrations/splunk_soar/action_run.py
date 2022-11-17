from automon.log import Logging

from .datatypes import AbstractDataType

log = Logging('ActionRun', level=Logging.CRITICAL)


class ActionRun(AbstractDataType):
    container: int = None
    id: int = None

    def __repr__(self):
        if self.id:
            return f'{self.id}'
        return f'{self.to_dict()}'
