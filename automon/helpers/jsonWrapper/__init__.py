import json


class Json(object):
    @staticmethod
    def dumps_dict(d, indent: int = None):
        return json.dumps({k: f'{v}' for k, v in d.items()}, indent=indent)
