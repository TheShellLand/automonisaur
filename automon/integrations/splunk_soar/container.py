import json
import datetime

from automon import Logging

from .common import Scaffolding

log = Logging('Container', level=Logging.CRITICAL)


class Container(Scaffolding):
    artifact_count: int
    start_time: datetime
    id: int

    def __init__(self, container: dict):
        self.artifact_count = None
        self.start_time = None
        self.id = None
        self.__dict__.update(container)

    def __repr__(self):
        if len(self.to_json()) > 100:
            return json.dumps(dict(
                name=self.name,
                label=self.label,
                status=self.status,
                id=self.id,
                artifact_count=self.artifact_count,
                create_time=self.create_time
            ))
        return self.to_json()
