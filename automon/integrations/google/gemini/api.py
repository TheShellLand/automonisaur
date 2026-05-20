try:
    from typing import Self
except:
    from typing_extensions import Self

from automon.helpers import *
from automon.helpers.loggingWrapper import LoggingClient, DEBUG
from automon.helpers.dictWrapper import DictHelper
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


class Part(DictHelper):
    text: str

    def __init__(self, part: dict | Self = None, text: str = ''):
        self._text: str = text

        super().__init__(part)

    def __repr__(self):
        return f"{len(self)} tokens :: {self.preview}"

    def __len__(self) -> int:
        return len(self.tokens)

    @property
    def text(self):
        self._text = str(self._text)
        return self._text

    @text.setter
    def text(self, value):
        self._text = str(value)

    @property
    def bytes(self):
        return self.text.encode()

    @property
    def tokens(self):
        return Tokens(self.text)

    @property
    def preview(self):
        return self.text[:120]


class Content(DictHelper):
    parts: list[Part]
    role: str

    def __init__(self, content: dict = None, role: str = 'user'):

        self.role = role
        self._parts = []

        super().__init__(content)

    def __repr__(self):
        return f"{len(self)} tokens"

    def __len__(self):
        return sum(len(x) for x in self.parts)

    def __bool__(self):
        if self.role and self.parts:
            return True
        return False

    @property
    def parts(self) -> list[Part]:
        if isinstance(self._parts, list):
            self._parts = encapsulate(value=self._parts, object_class=Part)
        return self._parts

    @parts.setter
    def parts(self, value):
        assert isinstance(value, list)
        self._parts = encapsulate(value=value, object_class=Part)

    def add_part(self, part: Part):
        assert isinstance(part, Part)
        self._parts.append(part)
        return self


class Candidate(DictHelper):
    content: Content
    avgLogprobs: float
    finishReason: str

    def __init__(self, candidate: dict = None):
        self._content = None

        super().__init__(candidate)

    @property
    def content(self) -> Content:
        self._content = encapsulate(value=self._content, object_class=Content)
        return self._content

    @content.setter
    def content(self, value):
        self._content = encapsulate(value=value, object_class=Content)


class GeminiPrompt(DictHelper):
    contents: list[Content]

    def __init__(self, prompt: dict = None):
        self._contents = []

        super().__init__(prompt)

    def __repr__(self):
        return f"{len(self)} tokens"

    def __len__(self) -> int:
        return sum(len(x) for x in self.contents)

    @property
    def contents(self):
        self._contents = encapsulate(value=self._contents, object_class=Content)
        return self._contents

    @contents.setter
    def contents(self, value):
        self._contents = encapsulate(value=value, object_class=Content)

    def add_content(self, content: Content):
        assert isinstance(content, Content)
        self._contents.append(content)
        return self

    def clear_history(self):
        self.contents = []
        return self

    def to_prompt(self):
        prompt = {'contents': []}
        for content in self.contents:
            parts = []
            for part in content.parts:
                parts.append({'text': part.text})
            prompt['contents'].append({'parts': parts})
        return prompt


class GeminiResponse(DictHelper):
    candidates: list[Candidate]
    usageMetadata: str
    modelVersion: str
    modelVersion: str

    def __init__(self, response: dict = None):

        self._candidates: list[dict] = []

        super().__init__(response)

    @property
    def candidates(self):
        value = self._candidates
        self._candidates = encapsulate(value=value, object_class=Candidate)
        return self._candidates

    @candidates.setter
    def candidates(self, value):
        self._candidates = encapsulate(value=value, object_class=Candidate)

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
