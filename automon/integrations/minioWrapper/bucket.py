import minio

from datetime import datetime

from automon.helpers.jsonWrapper import *


class Bucket(minio.datatypes.Bucket):
    name: str
    creation_date: datetime

    def __init__(self, bucket: minio.datatypes.Bucket):
        self.name: str = ''
        self.creation_date: datetime = None

        self.__dict__.update(bucket.__dict__)

    def to_json(self):
        return Json.dumps_dict(self.__dict__)

    def __repr__(self):
        return f'{str(self.creation_date)[:19]} ({self.name})'
