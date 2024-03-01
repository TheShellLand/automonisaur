from enum import Enum


class Api(object):
    api = f'api'


class Auth(object):
    api = f'{Api.api}/auth'
    token = f'{api}/token'
    user = f'{api}/user'

    def __init__(self, userId: str):
        self.userId = userId
        self.token = f'{self.userId}/token'
        self.create = f'{self.token}/create'


class ApplicationViewModels(Enum):
    """
    [
        {
            "id": "string",
            "name": "string",
            "acronym": "string",
            "description": "string",
            "createdDate": "string",
            "createdByUser": {
                "id": "string",
                "name": "string"
            },
            "modifiedDate": "string",
            "modifiedByUser": {
                "id": "string",
                "name": "string"
            }
        }
    ]
    """
    id: str
    name: str
    acronym: str
    description: str
    createdDate: str
    createdByUser: {
        "id": str,
        "name": str
    }
    modifiedDate: str
    modifiedByUser: {
        "id": str,
        "name": str
    }


class Application(object):
    api = f'{Api.api}/app'
    light = f'{api}/light'


class User(object):
    user = f'{Api.api}/user'
    login = f'{user}/login'


class Workspace(object):
    api = f'{Api.api}/workspaces'
    nav = f'{api}/nav'

    @classmethod
    def id(cls, id: int):
        """workspace specified by id"""
        return f'{cls.api}/{id}'

    @classmethod
    def app(cls, id: int):
        """workspaces for application id"""
        return f'{cls.api}/app/{id}'
