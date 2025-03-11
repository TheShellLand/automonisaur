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


class GeminiModels:

    @property
    def gemini_2_0_flash(self):
        """
        Next generation features, speed, and multimodal generation for a diverse variety of tasks

        input: Audio, images, videos, and text
        output: Text, images (coming soon), and audio (coming soon)
        """
        return f'gemini-2.0-flash'

    @property
    def gemini_2_0_flash_lite(self):
        """
        A Gemini 2.0 Flash model optimized for cost efficiency and low latency

        input: Audio, images, videos, and text
        output: Text
        """
        return f'gemini-2.0-flash-lite'

    @property
    def gemini_1_5_flash(self):
        """
        Fast and versatile performance across a diverse variety of tasks

        input: Audio, images, videos, and text
        output: Text
        """
        return f'gemini-1.5-flash'

    @property
    def gemini_1_5_flash_8b(self):
        """
        High volume and lower intelligence tasks

        input: Audio, images, videos, and text
        output: Text
        """
        return f'gemini-1.5-flash-8b'

    @property
    def gemini_1_5_pro(self):
        """
        Complex reasoning tasks requiring more intelligence

        input: Audio, images, videos, and text
        output: Text
        """
        return f'gemini-1.5-pro'

    @property
    def text_embedding_004(self):
        """
        Measuring the relatedness of text strings

        input: Text
        output: Text embeddings
        """
        return f'text-embedding-004'


class Part(DictUpdate):
    text: str

    def __init__(self, text: str = None):
        super().__init__()

        self.text = text


class Content(DictUpdate):
    parts: [Part]
    role: str

    def __init__(self):
        super().__init__()

        self.parts = []

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


class Candidate(DictUpdate):
    content: Content
    finishReason: str
    avgLogprobs: float

    def __init__(self):
        super().__init__()

    def enhance(self):
        if hasattr(self, 'content'):
            self.content = Content().update_dict(self.content)


class GeminiPrompt(DictUpdate):
    contents: [Content]

    def __init__(self):
        super().__init__()

        self.contents = []


class GeminiResponse(DictUpdate):
    candidates: [Candidate]
    usageMetadata: str
    modelVersion: str
    modelVersion: str

    def __init__(self):
        super().__init__()

    def enhance(self):

        if hasattr(self, 'candidates'):
            self.candidates = [Candidate().update_dict(x) for x in self.candidates]

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

    def to_string(self):
        return ''.join([x for x in self._get_chunks()])
