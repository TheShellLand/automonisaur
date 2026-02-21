class GoogleGeminiModels(object):
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

    def __init__(self):
        self.FREE_TIER = [
            self.gemini_flash_latest,
            # self.gemini_3_flash,
            # self.gemini_2_5_flash,
            # self.gemini_2_5_flash_exp,
            self.gemini_2_5_flash_lite,
            self.gemini_2_5_flash_live,
            # self.gemini_2_5_flash_preview_09_2025,
            # self.gemini_2_5_pro,
            # self.gemini_2_5_pro_1p_freebie,
            # self.gemini_2_0_flash,
            # self.gemini_2_0_flash_exp,
            # self.gemini_2_0_flash_lite,
            # self.gemini_2_0_flash_live,
            self.gemma_3_27b_it,
        ]

        self.PRO_TIER = [
            self.gemini_3_pro,
            self.gemini_3_pro_image,
            self.gemini_2_5_pro,
            self.gemini_2_5_pro_preview_tts,
            self.gemini_2_5_pro_exp_03_25,
            self.gemini_2_0_pro_exp_02_05,
        ]

        self.GEMMA = [
            self.gemma_3_27b,
            self.gemma_3_12b,
            self.gemma_3_7b,
        ]

        self.GEMINI_3 = [
            self.gemini_3_flash,
            self.gemini_3_pro,
            self.gemini_3_pro_image,
        ]

        self.GEMINI_2_5 = [
            self.gemini_2_5_flash,
            self.gemini_2_5_flash_lite,
            self.gemini_2_5_flash_live,
            self.gemini_2_5_flash_preview_tts,
            self.gemini_2_5_flash_exp,
            self.gemini_2_5_flash_preview_native_audio_dialog,
            self.gemini_2_5_flash_exp_native_audio_thinking_dialog,
            self.gemini_2_5_pro,
            self.gemini_2_5_pro_1p_freebie,
            self.gemini_2_5_pro_exp_03_25,
            self.gemini_2_5_pro_preview_tts,
            self.gemini_2_5_flash_preview_09_2025,
        ]

        self.GEMINI_2_0 = [
            self.gemini_2_0_flash,
            self.gemini_2_0_flash_lite,
            self.gemini_2_0_flash_live,
            self.gemini_2_0_flash_exp,
            self.gemini_2_0_flash_thinking_exp_01_21,
            self.gemini_2_0_pro_exp_02_05,
        ]

        self.GEMINI_1_5 = [
            # self.gemini_1_5_flash,
            self.gemini_1_5_flash_8b,
            self.gemini_1_5_pro,
            self.learnlm_1_5_pro_experimental,
        ]

        self.EMBEDDING = [
            self.gemini_embedding_exp_03_07,
        ]

        self.IMAGEN_3_0 = [
            self.imagen_3_0_generate_002,
        ]

        self.GEMINI_ALL = []

    @property
    def gemma_3_27b(self):
        return f'gemma-3-27b'

    @property
    def gemini_flash_latest(self):
        return f'gemini-flash-latest'

    @property
    def gemma_3_27b_it(self):
        return f'gemma-3-27b-it'

    @property
    def gemma_3_12b(self):
        return f'gemma-3-12b-it'

    @property
    def gemma_3_7b(self):
        return f'gemma-3-7b-it'

    @property
    def gemini_3_flash(self):
        return f'gemini-3-flash'

    @property
    def gemini_3_flash_preview(self):
        return f'gemini-3-flash-preview'

    @property
    def gemini_3_pro(self):
        return f'gemini-3-pro'

    @property
    def gemini_3_pro_image(self):
        return f'gemini-3-pro-image'

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
        raise Exception(f"model gemini-2.5-flash-preview-05-20 depreciated")

    @property
    def gemini_2_5_flash_preview_09_2025(self):
        """
        """
        return f'gemini-2.5-flash-preview-09-2025'

    @property
    def gemini_2_5_flash_preview_native_audio_dialog(self):
        """
        Audio, videos, and text
        Text and audio, interleaved	High quality, natural conversational audio outputs, with or without thinking
        """
        return f'gemini-2.5-flash-preview-native-audio-dialog'

    @property
    def gemini_2_5_flash_exp(self):
        return f'gemini-2.5-flash-exp'

    @property
    def gemini_2_5_flash_exp_native_audio_thinking_dialog(self):
        """
        Audio, videos, and text
        Text and audio, interleaved	High quality, natural conversational audio outputs, with or without thinking
        """
        return f'gemini-2.5-flash-exp-native-audio-thinking-dialog'

    @property
    def gemini_2_5_pro(self):
        """
        """
        return f'gemini-2.5-pro'

    @property
    def gemini_2_5_pro_1p_freebie(self):
        """
        """
        return f'gemini-2.5-pro-1p-freebie'

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
    def gemini_2_5_pro_preview_tts(self):
        """
        Audio, images, videos, and text
        Text	Enhanced thinking and reasoning, multimodal understanding, advanced coding, and more
        """
        return f'gemini-2.5-pro-preview-tts'

    @property
    def gemini_2_5_flash(self):
        """
        """
        return f'gemini-2.5-flash'

    @property
    def gemini_2_5_flash_lite(self):
        """
        """
        return f'gemini-2.5-flash-lite'

    @property
    def gemini_2_5_flash_live(self):
        """
        """
        return f'gemini-2.5-flash-live'

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
    def gemini_2_0_flash_exp(self):
        return f'gemini-2.0-flash-exp'

    @property
    def gemini_2_0_flash_live(self):
        """
        Next generation features, speed, and multimodal generation for a diverse variety of tasks

        input: Audio, images, videos, and text
        output: Text, images (coming soon), and audio (coming soon)
        """
        return f'gemini-2.0-flash-live'

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
