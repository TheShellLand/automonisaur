class V1(object):

    def __init__(self, host):
        self.endpoint = host

    @property
    def api(self):
        self.endpoint += '/api/v1'
        return self

    @property
    def validate(self):
        self.endpoint += '/validate'
        return self
