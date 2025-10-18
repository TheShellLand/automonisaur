import json


class DictUpdate(dict):

    def __init__(self):
        super().__init__()

    def _enhance(self):
        return self

    def enhance(self):
        import warnings
        warnings.warn(f"Method will be removed in a future release. Please use '_enhance' instead.")
        return self

    def __iter__(self):
        return self

    def __repr__(self):
        return f"{self.to_dict()}"

    def get(self, key, *args, **kwargs):
        return self.__dict__.get(key, *args, **kwargs)

    def update_dict(self, update: dict):
        if update is None:
            return self

        if hasattr(update, '__dict__'):
            update = update.__dict__

        assert type(update) == dict, f"ERROR :: {update=}"

        for key, value in update.items():
            setattr(self, key, value)

        self.enhance()
        self._enhance()
        return self

    def update_json(self, json_: str):
        self.update_dict(json.loads(json_))
        return self

    def to_dict(self):
        return self._to_dict(self)

    def to_json(self, indent: int = None):
        return json.dumps(self.to_dict(), indent=indent)

    def _to_dict(self, obj):

        if not hasattr(obj, "__dict__"):
            return obj

        result = {}
        for key, value in obj.__dict__.items():
            if key.startswith("_"):
                continue

            if type(value) is list:
                value = [self._to_dict(x) for x in value]
            else:
                value = self._to_dict(value)

            result[key] = value

        return result
