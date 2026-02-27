try:
    from typing import Self
except:
    from typing_extensions import Self

from automon.helpers.loggingWrapper import LoggingClient, DEBUG
from automon.helpers.dictWrapper import Dict
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

    def version(self, version: str):
        self.url += f'/{version}'
        return self

    def v1(self):
        return self.version('v1')

    def v1alpha(self):
        return self.version('v1alpha')

    def v1beta(self):
        return self.version('v1beta')

    def models(self, model: str):
        if 'models/' not in model:
            self.url += f'/models'

        if model:
            self.url += f'/{model}'

        return self

    def models_v1(self, model: str):
        pass

    def models_v1alpha(self, model: str):
        pass

    def models_v1beta(self, model: str):
        pass

    def list_models(self):
        """list all model modes"""
        self.url += ''
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

    def __init__(self, part: dict | Self = None, text: str = ''):
        super().__init__()

        self.text: str = text

        if part:
            self.automon_update(part)
            logger.debug(f"[Part] :: {self.bytes[:50]} :: {Tokens(self.text).count_pretty} tokens")

    def __repr__(self):
        return f"{len(self)} tokens"

    def __len__(self) -> int:
        return len(self.tokens)

    @property
    def bytes(self):
        return self.text.encode()

    @property
    def tokens(self):
        return Tokens(self.text)

    @property
    def preview(self):
        return f"{self.text}".encode()[:50]


class Content(Dict):
    parts: list[dict]
    role: str

    automon_parts: list[Part]

    def __init__(self, content: dict = None, role: str = 'user'):
        super().__init__()

        self.role: str = role
        self.parts: list[dict] = []

        if content:
            self.automon_update(content)

    def __repr__(self):
        return f"{len(self)} tokens"

    def __len__(self):
        return sum(len(x) for x in self.automon_parts)

    def __bool__(self):
        if self.role and self.parts:
            return True
        return False

    @property
    def automon_parts(self):
        return [Part(x) for x in self.parts]

    def add_part(self, part: Part):
        assert isinstance(part, Part)
        self.parts.append(part.to_dict())
        return self


class Candidate(Dict):
    content: dict
    avgLogprobs: float
    finishReason: str

    automon_content: Content

    def __init__(self, candidate: dict = None):
        super().__init__()

        self.content: dict = {}

        if candidate:
            self.automon_update(candidate)

    @property
    def automon_content(self) -> Content:
        return Content(self.content)


class GeminiPrompt(Dict):
    contents: list[Content]

    def __init__(self):
        super().__init__()

        self.contents: list[Content] = []

    def __repr__(self):
        return f"{len(self)} tokens"

    def __len__(self) -> int:
        return sum(len(x) for x in self.contents)

    def add_content(self, content: Content):
        assert isinstance(content, Content)
        self.contents.append(content)
        return self

    def clear_history(self):
        self.contents = []
        return self


class GeminiResponse(Dict):
    candidates: list[dict]
    usageMetadata: str
    modelVersion: str
    modelVersion: str

    automon_candidate: list[Candidate]

    def __init__(self, response: dict = None):
        super().__init__()

        self.candidates: list[dict] = []

        if response:
            self.automon_update(response)

    @property
    def automon_candidate(self) -> list[Candidate]:
        return [Candidate(x) for x in self.candidates]

    @property
    def response(self) -> Candidate | None:
        if self.automon_candidate:
            return self.automon_candidate[0]

    def _chunks(self):
        for chunk in self.automon_candidate:
            for part in chunk.automon_content.automon_parts:
                yield part.text

    def _chunks_list(self):
        chunks = []
        for chunk in self.automon_candidate:
            for part in chunk.automon_content.automon_parts:
                chunks.append(part.text)
        return chunks

    def print_stream(self):
        for chunk in self._chunks():
            print(f'{chunk}', end='', flush=True)
        print('\n', flush=True)
        return self

    def to_string(self):
        return ''.join([x for x in self._chunks()])
