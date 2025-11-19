try:
    from typing import Self
except:
    from typing_extensions import Self

from automon.helpers.loggingWrapper import LoggingClient, DEBUG
from automon.integrations.google.gmail.v1 import Dict
from automon.integrations.ollamaWrapper import Tokens

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


class GoogleGeminiApi(object):

    def __init__(self):
        self.url: str = ''

    @property
    def base(self):
        self.url = 'https://generativelanguage.googleapis.com'
        return self

    @property
    def v1beta(self):
        self.url += f'/v1beta'
        return self

    def models(self, model: str):
        self.url += f'/models/{model}'
        return self

    @property
    def generateContent(self):
        self.url += f':generateContent'
        return self

    def key(self, key: str):
        self.url += f'?key={key}'
        return self


class Part(Dict):
    text: str

    def __init__(self, part: dict | Self = None, text: str = None):
        super().__init__()

        self.text: str = text

        if part:
            self.automon_update(part)
            logger.debug(f"[Part] :: {Tokens().count(self.text)} tokens")


class Content(Dict):
    parts: list[Part]
    role: str

    def __init__(self, content: dict = None, role: str = 'user'):
        super().__init__()

        self.role: str = role
        self.parts: list[Part] = []

        if content:
            self.automon_update(content)

    def __bool__(self):
        if self.role and self.parts:
            return True
        return False

    def add_part(self, part: Part):
        assert isinstance(part, Part)
        self.parts.append(part)
        return self

    def _enhance(self):
        if self.parts:
            self.parts = [Part(x) for x in self.parts]


class Candidate(Dict):
    content: Content
    avgLogprobs: float
    finishReason: str

    def __init__(self, candidate: dict = None):
        super().__init__()

        self.content: Content = Content()

        if candidate:
            self.automon_update(candidate)

    def _enhance(self):
        if self.content:
            self.content = Content(self.content)


class GeminiPrompt(Dict):
    contents: list[Content]

    def __init__(self):
        super().__init__()

        self.contents: list[Content] = []

    def add_content(self, content: Content):
        assert isinstance(content, Content)
        self.contents.append(content)
        return self

    def clear_history(self):
        self.contents = []
        return self


class GeminiResponse(Dict):
    candidates: list[Candidate]
    usageMetadata: str
    modelVersion: str
    modelVersion: str

    def __init__(self, response: dict = None):
        super().__init__()

        self.candidates: list[Candidate] = []

        if response:
            self.automon_update(response)

    def _enhance(self):

        if self.candidates:
            self.candidates = [Candidate(x) for x in self.candidates]

    @property
    def response(self) -> Candidate | None:
        if self.candidates:
            return self.candidates[0]

    def _chunks(self):
        for chunk in self.candidates:
            for part in chunk.content.parts:
                yield part.text

    def _chunks_list(self):
        chunks = []
        for chunk in self.candidates:
            for part in chunk.content.parts:
                chunks.append(part.text)
        return chunks

    def print_stream(self):
        for chunk in self._chunks():
            print(f'{chunk}', end='', flush=True)
        print('\n', flush=True)
        return self

    def to_string(self):
        return ''.join([x for x in self._chunks()])
