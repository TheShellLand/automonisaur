import json

from automon.helpers.loggingWrapper import LoggingClient, DEBUG

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


class GoogleGeminiCandidate(object):

    def __init__(self, response: str):
        self.response = json.loads(response)

    @property
    def candidates(self):
        return self.response['candidates']

    def _get_chunks(self):
        for chunk in self.candidates:
            for part in chunk['content']['parts']:
                yield part['text']

    @property
    def usageMetadata(self):
        return self.response['usageMetadata']

    @property
    def modelVersion(self):
        return self.response['modelVersion']

    def print_stream(self):
        print('==========', flush=True)
        for chunk in self._get_chunks():
            print(f'{chunk}', end='', flush=True)
        print('==========', flush=True)
        return self
