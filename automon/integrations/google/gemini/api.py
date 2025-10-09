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
    """
    Current rate limits
    Free Tier
    Model	RPM	TPM	RPD
    Gemini 2.0 Flash	15	1,000,000	1,500
    Gemini 2.0 Flash-Lite	30	1,000,000	1,500
    Gemini 2.0 Pro Experimental 02-05	2	1,000,000	50
    Gemini 2.0 Flash Thinking Experimental 01-21	10	4,000,000	1,500
    Gemini 1.5 Flash	15	1,000,000	1,500
    Gemini 1.5 Flash-8B	15	1,000,000	1,500
    Gemini 1.5 Pro	2	32,000	50
    Imagen 3	--	--	--
    Gemini Embedding Experimental 03-07	5	--	100
    """

    @property
    def gemini_2_5_pro_exp_03_25(self):
        """
        Gemini 2.5 Pro Experimental
        Enhanced thinking and reasoning, multimodal understanding, advanced coding, and more

        input: Audio, images, videos, and text
        output: Text
        """
        return f'gemini-2.5-pro-exp-03-25'

    @property
    def gemini_2_5_flash_preview_tts(self):
        """
        Audio, images, videos, and text
        Text	Adaptive thinking, cost efficiency
        """
        return f'gemini-2.5-flash-preview-tts'

    @property
    def gemini_2_5_flash_preview_05_20(self):
        """
        Audio, images, videos, and text
        Text	Adaptive thinking, cost efficiency
        """
        return f'gemini-2.5-flash-preview-05-20'

    @property
    def gemini_2_5_flash_preview_native_audio_dialog(self):
        """
        Audio, videos, and text
        Text and audio, interleaved	High quality, natural conversational audio outputs, with or without thinking
        """
        return f'gemini-2.5-flash-preview-native-audio-dialog'

    @property
    def gemini_2_5_flash_exp_native_audio_thinking_dialog(self):
        """
        Audio, videos, and text
        Text and audio, interleaved	High quality, natural conversational audio outputs, with or without thinking
        """
        return f'gemini-2.5-flash-exp-native-audio-thinking-dialog'

    @property
    def gemini_2_5_pro_preview_tts(self):
        """
        Audio, images, videos, and text
        Text	Enhanced thinking and reasoning, multimodal understanding, advanced coding, and more
        """
        return f'gemini-2.5-pro-preview-tts'

    @property
    def gemini_2_5_pro_preview_05_06(self):
        """
        Audio, images, videos, and text
        Text	Enhanced thinking and reasoning, multimodal understanding, advanced coding, and more
        """
        return f'gemini-2.5-pro-preview-05-06'

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
    def gemini_2_0_flash_thinking_exp_01_21(self):
        """
        Gemini 2.0 Flash Thinking
        Reasoning for complex problems, features new thinking capabilities
        January 21, 2025
        """
        return f'gemini-2.0-flash-thinking-exp-01-21'

    @property
    def gemini_2_0_pro_exp_02_05(self):
        """
        Gemini 2.0 Pro
        Improved quality, especially for world knowledge, code, and long context
        February 5, 2025
        """
        return f'gemini-2.0-pro-exp-02-05'

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
    def learnlm_1_5_pro_experimental(self):
        """
        LearnLM 1.5 Pro Experimental

        Inputs: Audio, images, videos, and text
        Output: Text	November 19, 2024
        """
        return f'learnlm-1.5-pro-experimental'

    @property
    def text_embedding_004(self):
        """
        Measuring the relatedness of text strings

        input: Text
        output: Text embeddings
        """
        return f'text-embedding-004'

    @property
    def imagen_3_0_generate_002(self):
        """
        Imagen 3
        Our most advanced image generation model

        input: Text
        output: Images
        """
        return f'imagen-3.0-generate-002'

    @property
    def gemini_embedding_exp_03_07(self):
        """
        Gemini
        Our first Gemini based embedding model
        March 7, 2025
        """
        return f'gemini-embedding-exp-03-07'


class Part(DictUpdate):
    text: str

    def __init__(self, text: str = None):
        super().__init__()

        self.text = text


class Content(DictUpdate):
    parts: [Part]
    role: str

    def __init__(self, role: str = 'user'):
        super().__init__()

        self.role = role
        self.parts = []

    def add_part(self, part: Part):
        self.parts.append(part)
        return self

    def enhance(self):
        if hasattr(self, 'parts'):
            self.parts = [Part().update_dict(x) for x in self.parts]


class Candidate(DictUpdate):
    content: Content
    avgLogprobs: float
    finishReason: str

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

    def add_content(self, content: Content):
        self.contents.append(content)
        return self

    def clear_history(self):
        self.contents = []
        return self


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
            chunk = Candidate().update_dict(chunk)
            for part in chunk.content.parts:
                yield part.text

    def print_stream(self):
        for chunk in self._get_chunks():
            print(f'{chunk}', end='', flush=True)
        print('\n', flush=True)
        return self

    def to_string(self):
        return ''.join([x for x in self._get_chunks()])
