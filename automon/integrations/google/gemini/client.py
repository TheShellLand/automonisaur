import sys
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

# Platform-specific setup
try:
    import msvcrt


    def get_keypress():
        if msvcrt.kbhit():
            return msvcrt.getch()
        return None


    # Windows usually maps SHIFT-ENTER to standard carriage return in basic buffers,
    # but some terminals send \x0d.
    SHIFT_ENTER = b'\x0d'

except ImportError:
    import termios
    import tty


    def get_keypress():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


    # Unix SHIFT-ENTER escape sequence (varies by terminal, \n is common)
    SHIFT_ENTER = '\n'

from automon.integrations.ollamaWrapper import prompt_templates


class GoogleGeminiClient(object):
    models = GoogleGeminiModels()
    models_search = {}

    prompts = prompt_templates
    api = GoogleGeminiApi()

    def __init__(
            self,
            config: GoogleGeminiConfig = None,
            model: str = None,
            api_version: str = None
    ):
        self.config = config or GoogleGeminiConfig()
        self.model = model
        self.api_version = api_version

        self._requests = RequestsClient()

        self._prompt = GeminiPrompt()
        self._chat: GeminiResponse = None

        self.models_in_use = self.models.FREE_TIER

        if self.model and self.api_version:
            self._check_model()

    def __repr__(self):
        return f"[GoogleGeminiClient] :: {len(self)} tokens"

    def __len__(self) -> int:
        return len(self._prompt)

    def _agent_download(self, message: str) -> str:

        url = message[len('/download'):].strip()

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

        return download

    def _list_models(self, version: str = 'v1beta'):
        if version not in self.models_search:
            key = self.config.random_api_key()
            url = self.api.base.version(version).models('').key(key=key).url
            models = self._requests.get_self(url=url).to_dict()
            self.models_search[version] = [Model(x) for x in models['models']]
        return self

    def _list_models_v1(self):
        return self._list_models(version='v1')

    def _list_models_v1alpha(self):
        return self._list_models(version='v1alpha')

    def _list_models_v1beta(self):
        return self._list_models(version='v1beta')

    def _find_model_all(self, model: str = None) -> dict:
        self._list_models_v1()
        self._list_models_v1alpha()
        self._list_models_v1beta()

        models = {}
        for api, models_ in self.models_search.items():
            if model:
                models[api] = [x for x in models_ if model in x.name]
            else:
                models[api] = models_

        return models

    def _check_model(self, api: str = None, model: str = None) -> bool:
        if not api:
            api = self.api_version

        if not model:
            model = self.model

        model = model.split('/')[-1]

        assert api and model

        self._list_models(version=api)
        for model_ in self.models_search[api]:
            if model == model_.name.split('/')[-1]:
                return True
        raise Exception(f"[GoogleGeminiClient] :: ERROR :: Model {model} not found in {api}")

    def add_content(self, prompt: str, role: str = 'user'):
        if not isinstance(prompt, str):
            return self

        part = Part(text=prompt)
        content = Content(role=role).add_part(part=part)
        self._prompt.add_content(content=content)

        content_len = len(Tokens(string=prompt))
        logger.debug(f"[GoogleGeminiClient] :: "
                     f"add_content :: "
                     f"{part.preview} :: "
                     f"{content_len:,} tokens ({len(self)} total)")
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
        self._check_model()

        url = self.api.base.version(self.api_version).models(self.model).generateContent.key(
            key=self.config.random_api_key()).url
        json = self._prompt.to_dict()
        chat = self._requests.post(url=url, json=json, headers=self.config.headers())

        if not chat:
            logger.error(f'[GoogleGeminiClient] :: chat :: ERROR :: {self.model} :: {self._requests.to_dict()}')
            raise Exception(f'[GoogleGeminiClient] :: chat :: ERROR :: {self.model} :: {self._requests.to_dict()}',
                            self.model)

        self._chat = GeminiResponse(self._requests.to_dict())

        if print_stream:
            self._chat.print_stream()

        self._prompt.add_content(self._chat.response.automon_content)
        return self

    def chat_forever(self):

        while True:
            prompt = ''
            lines = []

            print(f"INPUT (send with CTRL+C) or /SEND: ")
            while True:
                try:
                    line = input()

                    if line.strip().lower() == '/send':
                        break

                    if line.strip().lower() == '/exit':
                        logger.info(f"[GoogleGeminiClient] :: chat_forever :: done")
                        return self

                    lines.append(line)
                except KeyboardInterrupt:
                    break

            if lines:
                prompt = prompt.join(lines)

            if not prompt:
                continue

            if prompt.strip().lower() == '/clear':
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

    def set_model(self, model: Model, api_version: str):
        self.model = model.name
        self.api_version = api_version
        logger.debug(f"[GoogleGeminiClient] :: set_model:: {api_version} :: {model.name}")
        return self

    def set_random_model(self):
        if not self.models_search:
            self._find_model_all()

        models = []
        for api, models_ in self.models_search.items():
            for model in models_:
                models.append((api, model))

        api, model = random.choice(models)
        return self.set_model(model=model, api_version=api)

    def reponse_is_true(self, response: str) -> bool | None:
        if 'true' in response.lower():
            return True
        if 'false' in response.lower():
            return False
        raise Exception(f"[GoogleGeminiClient] :: reponse_is_true :: neither true or false")

    def response_is_false(self, response: str) -> bool | None:
        if 'false' in response.lower():
            return True
        if 'true' in response.lower():
            return False
        raise Exception(f"[GoogleGeminiClient] :: response_is_false :: neither true or false")
