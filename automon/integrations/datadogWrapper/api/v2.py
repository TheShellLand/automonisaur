class V2(object):

    def __init__(self, host):
        self.endpoint = host

    @property
    def api(self):
        self.endpoint += '/api/v2'
        return self
