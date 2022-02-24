import json


class Artifact:
    def __init__(self, artifact: dict):
        self.__dict__.update(artifact)

    def __repr__(self):
        return self.to_json()

    def __len__(self):
        return len(self.to_json())

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v}

    def to_json(self):
        return json.dumps(self.to_dict())
