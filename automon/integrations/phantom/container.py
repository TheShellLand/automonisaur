import json


class Container:
    def __init__(self, container: dict):
        self.artifact_count = None
        self.start_time = None
        self.id = None
        self.__dict__.update(container)

    def __repr__(self):
        if self.__len__() > 100:
            return f'{{' \
                   f'name={self.name}, ' \
                   f'label={self.label}, ' \
                   f'status={self.status}, ' \
                   f'id={self.id}, ' \
                   f'artifacts={self.artifact_count}, ' \
                   f'created={self.start_time}}} '
        return self.to_json()

    def __len__(self):
        return len(self.to_json())

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v}

    def to_json(self):
        return json.dumps(self.to_dict())
