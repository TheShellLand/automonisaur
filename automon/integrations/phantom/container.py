import json
import datetime

from dateutil import parser

from automon import Logging

log = Logging('Container', level=Logging.CRITICAL)


class Container:
    def __init__(self, container: dict):
        self.artifact_count = None
        self.start_time = None
        self.id = None
        self.__dict__.update(container)

    def __repr__(self):
        if self.__len__() > 100:
            return json.dumps(dict(
                name=self.name,
                label=self.label,
                status=self.status,
                id=self.id,
                artifact_count=self.artifact_count,
                start_time=self.start_time
            ))
        return self.to_json()

    def __len__(self):
        return len(self.to_json())

    def __lt__(self, other):
        return self._created() < other._created()

    def _parse_timestamp(self, timestamp: str) -> datetime.datetime:
        """parse string into datetime object

        :timestamp: '2020-02-18T15:50:58.903568Z'
        :returns: datetime.datetime(2020, 2, 18, 15, 50, 58, 903568, tzinfo=tzutc())
        """
        return parser.parse(timestamp)

    def _created(self):
        return self._parse_timestamp(self.start_time)

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v}

    def to_json(self):
        return json.dumps(self.to_dict())
