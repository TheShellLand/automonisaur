import splunklib.client as client

from automon.integrations.splunk.config import SplunkConfig


class SplunkClient:
    def __init__(self):
        self.config = SplunkConfig()
        self.client = client.connect(
            host=self.config.host,
            port=self.config.port,
            username=self.config.username,
            password=self.config.password)

        # referred to as a service in docs
        self.service = self.client
        assert isinstance(self.service, client.Service)

        self.apps = self.client.apps

    def get_client(self):
        return self.client

    def get_service(self):
        return self.client.connect()

    def get_apps(self):
        return [x for x in self.service.apps]


    def create_app(self, app_name):
        return self.apps.create(app_name)

    def get_app(self, app_name):
        return self.apps[app_name]

    def delete_app(self, app_name):
        return self.apps.delete(app_name)

    def app_info(self, app_name):
        return f'{self.apps[app_name]}'


    def __str__(self):
        return f'{self.client}'
