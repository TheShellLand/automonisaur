import json
import random
import readline

import automon.integrations.seleniumWrapper
import automon.integrations.ollamaWrapper.prompt_templates

from automon.helpers.loggingWrapper import LoggingClient, DEBUG
from automon.integrations.requestsWrapper import RequestsClient
from automon.integrations.ollamaWrapper import Tokens

from .api import *
from .models import *
from .config import GoogleGeminiConfig

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


class GoogleGeminiClient(object):
    models = GoogleGeminiModels()
    prompts = automon.integrations.ollamaWrapper.prompt_templates.AgentTemplates()

    def __init__(self, config: GoogleGeminiConfig = None, model: GoogleGeminiModels = None):
        self.config = config or GoogleGeminiConfig()
        self.model = model or self.models.gemini_2_0_flash

        self._requests = RequestsClient()

        self._prompt = GeminiPrompt()
        self._chat: GeminiResponse = None

        self.models_in_use = self.models.FREE_TIER

    def __repr__(self):
        return f"[GoogleGeminiClient] :: {self.config=}"

    def _agent_download(self, message: str) -> str:
        logger.debug(f'[GoogleGeminiClient] :: _agent_download :: >>>>')

        download = message[len('/download'):].strip()
        url = download

        print(f":: SYSTEM :: downloading {url} ::")

        browser = automon.integrations.seleniumWrapper.SeleniumBrowser().set_webdriver_wrapper(
            automon.integrations.seleniumWrapper.ChromeWrapper().enable_defaults()
        )
        browser.start()
        browser.get(url=url)
        browser.refresh()
        browser.refresh()
        download = f"{browser.get_page_source_beautifulsoup().html}"
        # download = browser.get_page_source_beautifulsoup().html.text
        browser.quit()

        logger.info(f'[GoogleGeminiClient] :: _download :: done')
        return download

    def add_content(self, prompt: str, role: str = 'user'):
        if not isinstance(prompt, str):
            return self

        part = Part(text=prompt)
        content = Content(role=role).add_part(part=part)
        self._prompt.add_content(content=content)

        content_len = Tokens(string=prompt).count
        logger.debug(f"[GoogleGeminiClient] :: add_content :: {content_len:,} tokens")
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

        url = GoogleGeminiApi().base.v1beta.models(self.model).generateContent.key(key=self.config.random_api_key()).url
        json = self._prompt.to_dict()
        chat = self._requests.post(url=url, json=json, headers=self.config.headers())

        if not chat:
            raise Exception(f'[GoogleGeminiClient] :: chat :: ERROR :: {self.model} :: {self._requests.to_dict()}')

        self._chat = GeminiResponse(self._requests.to_dict())

        if print_stream:
            self._chat.print_stream()

        self._prompt.add_content(self._chat.response.automon_content)
        return self

    def chat_forever(self):

        while True:
            prompt = ''
            lines = []

            print(f"INPUT (end prompt with /send): ")
            while True:

                try:
                    line = input()
                    if line.strip() == '/send':
                        break
                    if line.strip() == '/exit':
                        return self

                    lines.append(line)

                except KeyboardInterrupt:
                    logger.info(f"[GoogleGeminiClient] :: chat_forever :: done")
                    return self

            if lines:
                prompt = prompt.join(lines)
                prompt = prompt.strip()

            if not prompt:
                continue

            if prompt == '/exit':
                logger.info(f"[GoogleGeminiClient] :: chat_forever :: done")
                return self

            if prompt == '/clear':
                self._prompt.clear_history()
                continue

            if '/download' in prompt[:len('/download')]:
                prompt = self._agent_download(message=prompt)
                self.add_content(prompt=prompt)
                continue

            self.add_content(prompt=prompt).chat()

    def chat_response(self) -> str:
        return self._chat.to_string()

    def is_ready(self) -> bool:
        if self.model and self.config.is_ready():
            return True
        logger.error(f'[GoogleGeminiClient] :: is_ready :: ERROR')
        return False

    def set_model(self, model: GoogleGeminiModels):
        self.model = model
        logger.debug(f"[GoogleGeminiClient] :: set_model :: {model=}")
        return self

    def set_random_model(self):
        return self.set_model(random.choice(self.models_in_use))

    def reponse_is_true(self, response: str) -> bool | None:
        if 'true' in response.lower():
            return True
        if 'false' in response.lower():
            return False
        logger.error(f"[GoogleGeminiClient] :: reponse_is_true :: neither true or false")

    def response_is_false(self, response: str) -> bool | None:
        if 'false' in response.lower():
            return True
        if 'true' in response.lower():
            return False
        logger.error(f"[GoogleGeminiClient] :: response_is_false :: neither true or false")
