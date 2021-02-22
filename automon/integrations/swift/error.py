class SwiftError_(object):
    def __init__(self, error: dict):
        self.action = error.get('action', '')
        self.container = error.get('container', '')
        self.headers = error.get('headers', '')
        self.success = error.get('success', '')
        self.error = error.get('error', '')
        self.traceback = error.get('traceback', '')
        self._tb = self.traceback
        self.error_timestamp = error.get('error_timestamp', '')
        self.response_dict = error.get('response_dict', '')

    def __str__(self):
        return (
            f'Error:\n'
            f'>*Action*: {self.action}\n'
            f'>*Container*: {self.container}\n'
            f'>*Error*: {self.error}\n'
            f'Traceback: \n```{self.traceback}```'
        )
