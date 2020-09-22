import splunklib.client as client

from automon.log import Logging
from automon.integrations.splunk.config import SplunkConfig


class SplunkClient:
    _log = Logging('SplunkClient', level=Logging.DEBUG)

    def __init__(self, config: SplunkConfig = SplunkConfig()):

        self.config = config
        try:
            self.client = client.connect(
                host=self.config.host,
                port=self.config.port,
                username=self.config.username,
                password=self.config.password,
                verify=self.config.verify,
                scheme=self.config.scheme,
                app=None,
                owner=None,
                token=None,
                cookie=None
            )

            # referred to as a service in docs
            self.service = self.client
            assert isinstance(self.service, client.Service)

        except Exception as e:
            self.client = False

    def info(self):
        return f'{self}'

    def get_apps(self):
        return [Application(x) for x in self.service.apps]

    def create_app(self, app_name):
        return self.apps.create(app_name)

    def get_app(self, app_name):
        return self.apps[app_name]

    def delete_app(self, app_name):
        return self.apps.delete(app_name)

    def app_info(self, app_name):
        return f'{self.service.apps[app_name]}'

    def __str__(self):
        if self.client:
            return f'connected to {self.config}'
        return f'not connected to {self.config}'


class Application:
    def __init__(self, object):
        self._app = object

        self.access = object['access']
        self.content = object['content']
        self.defaults = object['defaults']
        self.fields = object['fields']
        self.links = object['links']
        self.name = object['name']
        self.path = object['path']
        self.service = object['service']
        self.setupInfo = object['setupInfo']
        self.state = object['state']

        self._state = object['_state']
