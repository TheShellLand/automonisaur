from automon.integrations.google.gmail.v1 import DictUpdate


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

    @property
    def models(self):
        self.url += f'/models'
        return self

    @property
    def gemini(self):
        self.url += f'/gemini-1.5-flash'
        return self

    @property
    def generateContent(self):
        self.url += f':generateContent'
        return self

    def key(self, key: str):
        self.url += f'?key={key}'
        return self


class Part(DictUpdate):
    text: str

    def __init__(self):
        super().__init__()


class Content(DictUpdate):
    parts: [Part]
    role: str

    def __init__(self):
        super().__init__()

    def enhance(self):
        if hasattr(self, 'parts'):
            self.parts = [Part().update_dict(x) for x in self.parts]


class Chunk(DictUpdate):
    content: Content
    avgLogprobs: float
    finishReason: str

    def __init__(self):
        super().__init__()

    def enhance(self):
        if hasattr(self, 'content'):
            self.content = Content().update_dict(self.content)


class GoogleGeminiCandidate(DictUpdate):
    candidates: list
    usageMetadata: str
    modelVersion: str
    modelVersion: str

    def __init__(self):
        super().__init__()

    def _get_chunks(self):
        for chunk in self.candidates:
            chunk = Chunk().update_dict(chunk)
            for part in chunk.content.parts:
                yield part.text

    def print_stream(self):
        for chunk in self._get_chunks():
            print(f'{chunk}', end='', flush=True)
        print('\n', flush=True)
        return self
