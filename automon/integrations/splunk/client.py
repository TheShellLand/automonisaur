import splunklib.client as client


class SplunkClient(client):
    def __init__(self, host: str = 'localhost', port: int = 8089,
                 username: str = 'admin', password: str = ''):
        self.host = host
        self.port = port
        self.username = username

        self.service = client.connect(
            host=host, port=port,
            username=username, password=password)

        self.apps = self.service.apps

        assert isinstance(self.service, client.Service)

    def create_app(self, app_name):
        return self.apps.create(app_name)

    def get_app(self, app_name):
        return self.apps[app_name]

    def delete_app(self, app_name):
        return self.apps.delete(app_name)

    def app_info(self, app_name):
        return f'{self.apps[app_name]}'
