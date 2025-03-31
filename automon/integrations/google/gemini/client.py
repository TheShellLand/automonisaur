import json
import readline

import automon.integrations.ollamaWrapper.prompt_templates

from automon.helpers.loggingWrapper import LoggingClient, DEBUG
from automon.integrations.requestsWrapper import RequestsClient

from .api import *
from .config import GoogleGeminiConfig

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


class GoogleGeminiClient(object):
    models = GeminiModels()
    prompts = automon.integrations.ollamaWrapper.prompt_templates.AgentTemplates()

    def __init__(self, config: GoogleGeminiConfig = None, model: GeminiModels = None):
        self.config = config or GoogleGeminiConfig()
        self.model = model or self.models.gemini_2_0_flash

        self._requests = RequestsClient()

        self._prompt = GeminiPrompt()
        self._chat: GeminiResponse = None

    def __repr__(self):
        return f"[GoogleGeminiClient] :: {self.config=}"

    def add_content(self, prompt: str, role: str = 'user'):
        if type(prompt) is not str:
            return self

        part = Part(text=prompt)
        content = Content(role=role).add_part(part=part)
        self._prompt.add_content(content=content)

        logger.debug(f"[GoogleGeminiClient] :: add_content :: {content=}")
        logger.info(f"[GoogleGeminiClient] :: add_content :: done")
        return self

    @property
    def chat_contents(self):
        return self._prompt.contents

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

        url = GoogleGeminiApi().base.v1beta.models(self.model).generateContent.key(key=self.config.random_key()).url
        json = self._prompt.to_dict()
        chat = self._requests.post(url=url, json=json, headers=self.config.headers())

        if not chat:
            raise Exception(f'[GoogleGeminiClient] :: chat :: ERROR :: {self._requests.content}')

        self._chat = GeminiResponse().update_json(self._requests.content)

        if print_stream:
            self._chat.print_stream()

        self._prompt.add_content(self._chat.candidates[0].content)
        logger.info(f"[GoogleGeminiClient] :: chat :: done")
        return self

    def chat_forever(self):

        while True:

            prompt = ''
            try:
                prompt += input(f"\n$> ")
                prompt = prompt.strip()
            except KeyboardInterrupt:
                logger.info(f"[GoogleGeminiClient] :: chat_forever :: done")
                return self

            if not prompt:
                continue

            if prompt == '/exit':
                logger.info(f"[GoogleGeminiClient] :: chat_forever :: done")
                return self

            if prompt == '/clear':
                self._prompt.clear_history()
                continue

            self.add_content(prompt=prompt).chat()

    def chat_response(self) -> str:
        return self._chat.to_string()

    def is_ready(self):
        if self.config.is_ready():
            return True
        logger.error(f'[GoogleGeminiClient] :: is_ready :: ERROR')
        return False

    def set_model(self, model: GeminiModels):
        logger.debug(f"[GoogleGeminiClient] :: set_model :: {model=}")
        self.model = model
        logger.info(f"[GoogleGeminiClient] :: set_model :: done")
        return self

    def true_or_false(self, response: str):
        if 'true' in response.lower():
            return True
        if 'false' in response.lower():
            return False

        logger.error(f"[GoogleGeminiClient] :: true_or_false :: neither true or false")
