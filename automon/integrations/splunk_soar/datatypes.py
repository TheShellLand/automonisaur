import json
import datetime

from dateutil import parser

from automon.log import Logging

log = Logging('AbstractDataType', level=Logging.DEBUG)


class AbstractDataType:
    def __init__(self, data: dict):
        self.__dict__.update(data)

    def __repr__(self):
        return self.to_json()

    def __len__(self):
        return self.id

    def __lt__(self, other):
        return self._created() < other._created()

    def _created(self):
        return self._parse_timestamp(self.create_time)

    def _parse_timestamp(self, timestamp: str) -> datetime.datetime:
        """parse string into datetime object

        :timestamp: '2020-02-18T15:50:58.903568Z'
        :returns: datetime.datetime(2020, 2, 18, 15, 50, 58, 903568, tzinfo=tzutc())
        """
        return parser.parse(timestamp)

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v}

    def to_json(self):
        return json.dumps(self.to_dict())
