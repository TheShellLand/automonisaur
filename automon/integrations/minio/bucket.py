import json

from minio.datatypes import Bucket as MinioBucket


class Bucket(MinioBucket):
    def __init__(self, bucket: MinioBucket):
        self.__dict__.update(bucket.__dict__)

    def to_json(self):
        return json.dumps({k: f'{v}' for k, v in self.__dict__.items()})
