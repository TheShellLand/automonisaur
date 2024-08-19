import json


class ServiceNow:
    table: str = None

    def __repr__(self):
        return f'{self.__dict__}'

    @property
    def fields(self):
        return self.to_json()

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v}

    def to_json(self):
        return json.dumps(self.to_dict())
