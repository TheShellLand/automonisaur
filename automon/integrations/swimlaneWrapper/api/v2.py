class Api(object):
    api = f'api'


class User(object):
    user = f'{Api.api}/user'
    login = f'{user}/login'


class Auth(object):

    def __init__(self, userId: str):
        self.auth = f'{Api.api}/auth'

        self.token = f'{self.auth}/token'
        self.create = f'{self.token}/create'

        self.user = f'{self.auth}/user'
        self.userId = userId
        self.token = f'{userId}/token'
