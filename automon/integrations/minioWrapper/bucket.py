import json
import minio


class Bucket(minio.datatypes.Bucket):
    def __init__(self, bucket: minio.datatypes.Bucket):
        self.__dict__.update(bucket.__dict__)

    def to_json(self):
        return json.dumps({k: f'{v}' for k, v in self.__dict__.items()})
