import minio

from datetime import datetime

from automon.helpers.jsonWrapper import *
from automon.helpers.dictWrapper import *


class Bucket(Dict):
    name: str
    creation_date: datetime

    def __init__(self, bucket: minio.datatypes.Bucket = None):
        super().__init__()

        self.name: str = ''
        self.creation_date: datetime = None

        if bucket:
            self.name = bucket.name
            self.creation_date = bucket.creation_date

    def __repr__(self):
        return f'{str(self.creation_date)[:19]} ({self.name})'

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, Bucket):
            return self.name == other.name
        if isinstance(other, str):
            return self.name == other
        return NotImplemented

    def __lt__(self, other):
        if self.creation_date:
            if self.creation_date < other.creation_date:
                return True
        return False

    def to_json(self):
        return Json.dumps_dict(self.__dict__)
