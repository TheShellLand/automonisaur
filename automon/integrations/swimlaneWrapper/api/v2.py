from enum import Enum


class Api(object):
    api = f'api'


class Auth(object):
    api = f'{Api.api}/auth'
    user = f'{api}/user'
    token = f'{api}/token'
    create = f'{token}/create'

    @classmethod
    def delete(cls, userId: str):
        return f'{cls.user}/{userId}/token'

    @classmethod
    def metadata(cls, userId: str):
        return f'{cls.user}/{userId}/token'


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


class Record(object):

    @classmethod
    def api(cls, appId: str):
        return f'{Application.api}/{appId}/record'

    @classmethod
    def get(cls, appId: str, id: str):
        return f'{cls.api(appId)}/{id}'


class User(object):
    api = f'{Api.api}/user'
    login = f'{api}/login'


class Workspace(object):
    api = f'{Api.api}/workspaces'
    nav = f'{api}/nav'

    @classmethod
    def id(cls, id: str):
        """workspace specified by id"""
        return f'{cls.api}/{id}'

    @classmethod
    def app(cls, id: str):
        """workspaces for application id"""
        return f'{cls.api}/app/{id}'
