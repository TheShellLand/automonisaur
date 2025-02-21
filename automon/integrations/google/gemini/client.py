import json

from automon.helpers.loggingWrapper import LoggingClient, DEBUG
from automon.integrations.requestsWrapper import RequestsClient

from .api import GoogleGeminiApi
from .config import GoogleGeminiConfig
from .candidate import GoogleGeminiCandidate

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


class GoogleGeminiClient(object):

    def __init__(self, config: GoogleGeminiConfig = None):
        self.config = config or GoogleGeminiConfig()

        self._requests = RequestsClient()

        self._prompt = {
            "contents": []
        }

        self._candidate = None

    def __repr__(self):
        return f"[GoogleGeminiClient] :: {self.config=}"

    def add_content(self, content: str):
        parts = {
            "parts": [{"text": content}]
        }
        self.chat_contents.append(parts)
        return self

    @property
    def chat_contents(self):
        return self._prompt['contents']

    def chat(self, print_stream: bool = True, **kwargs):
        """

        curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=GEMINI_API_KEY" \
        -H 'Content-Type: application/json' \
        -X POST \
        -d '{
          "contents": [{
            "parts":[{"text": "Explain how AI works"}]
            }]
           }'


        """

        url = GoogleGeminiApi().base.v1beta.models.gemini.generateContent.key(key=self.config.api_key).url
        data = json.dumps(self._prompt)
        chat = self._requests.post(url=url, data=data, headers=self.config.headers())

        if not chat:
            raise Exception(f'[GoogleGeminiClient] :: chat :: ERROR :: {self._requests.content}')

        self._candidate = GoogleGeminiCandidate(self._requests.content)

        if print_stream:
            self._candidate.print_stream()

        return self

    def is_ready(self):
        if self.config.is_ready():
            logger.info(f'[GoogleGeminiClient] :: is_ready :: done')
            return True
