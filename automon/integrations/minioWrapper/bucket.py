import json
import minio

from datetime import datetime


class Bucket(minio.datatypes.Bucket):
    name: str
    creation_date: datetime

    def __init__(self, bucket: minio.datatypes.Bucket):
        self.__dict__.update(bucket.__dict__)

    def to_json(self):
        return json.dumps({k: f'{v}' for k, v in self.__dict__.items()})

    def __repr__(self):
        return f'{str(self.creation_date)[:19]} ({self.name})'
