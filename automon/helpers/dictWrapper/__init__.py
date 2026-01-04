import json


class Dict(dict):

    def __init__(self):
        super().__init__()

    def _enhance(self):
        return self

    def enhance(self):
        import warnings
        warnings.warn(f"[Dict] :: Method will be removed in a future release. Please use '_enhance' instead.")
        return self

    def __iter__(self):
        return self

    def __repr__(self):
        return f"{self.to_dict()}"

    def automon_update(self, update: dict | str | object | None):

        if update is None:
            return self

        if isinstance(update, str):
            return self._update_json(update)

        if hasattr(update, '__dict__'):
            update = update.__dict__

        if isinstance(update, dict):
            return self._update_dict(update)

        raise Exception(f"[Dict] :: automon_update :: ERROR :: {update=}")

    def _update_dict(self, update: dict):

        for key, value in update.items():
            setattr(self, key, value)

        self.enhance()
        self._enhance()
        return self

    def _update_json(self, update: str):
        return self._update_dict(json.loads(update))

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

    def to_dict(self):
        if self.to_json():
            return self._to_dict(self)

    def to_json(self, indent: int = None):
        return json.dumps(self._to_dict(self), indent=indent)
