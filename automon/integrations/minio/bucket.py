import json

from minio.datatypes import Bucket as MinioBucket


class Bucket(MinioBucket):
    def __init__(self, bucket: MinioBucket):
        self.__dict__.update(bucket.__dict__)

    def __repr__(self):
        return f'{self.name}'

    def __str__(self):
        return f'{self.name}'

    def __eq__(self, other):
        if isinstance(other, Bucket):
            return self.name == other.name
        if isinstance(other, str):
            return self.name == other
        return NotImplemented

    def __hash__(self):
        return hash(self.name)

    @property
    def creation_date(self):
        return self._creation_date

    @property
    def name(self):
        return self._name

    def to_dict(self):
        return self.__dict__

    def to_json(self):
        return json.dumps({k: f'{v}' for k, v in self.to_dict().items()})
