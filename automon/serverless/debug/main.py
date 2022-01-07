import json


def request_dict(requests):
    return f'{requests.__dict__}'


def request_as_json(requests):
    return f"{json.dumps(requests.__dict__)}"
