import json

import minio.datatypes


class Bucket(minio.datatypes.Bucket):
    def __init__(self, bucket: minio.datatypes.Bucket):
        self.__dict__.update(bucket.__dict__)

    def __repr__(self):
        return f'{self.to_json}'

    @property
    def creation_date(self):
        return self._creation_date

    @property
    def name(self):
        return self._name

    def to_dict(self):
        return self.__dict__

    def to_json(self):
        return json.dumps(self.to_dict())
