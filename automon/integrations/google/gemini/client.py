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
    _models = GoogleGeminiModels()
    _models_search = {}

    _templates = prompt_templates
    _api = GoogleGeminiApi()

    def __init__(
            self,
            config: GoogleGeminiConfig = None,
            model: str = None,
            api_version: str = None
    ):
        self.model = model
        self.api_version = api_version
        self._config = config or GoogleGeminiConfig()

        self._prompt = GeminiPrompt()
        self._chat: GeminiResponse = None

        self.models_in_use = self._models.FREE_TIER

        self._requests = RequestsClient()

        if self.model and self.api_version:
            self._check_model()

    def __repr__(self):
        return repr_str([
            f"[GoogleGeminiClient]",
            self.api_version,
            self.model,
            f'{len(self)} tokens',
        ])

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
        if version not in self._models_search:
            key = self._config.random_api_key()
            url = self._api.base.version(version).models('').key(key=key).url
            models = self._requests.get(url=url).to_dict()
            self._models_search[version] = [Model(x) for x in models.get('models', [])]
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
        for api, models_ in self._models_search.items():
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
        for model_ in self._models_search[api]:
            model_ = model_.name.split('/')[-1]
            if model_ == model:
                return True
        raise debug_exception(locals(), f'{api}/{model} not found')

    def add_content(self, prompt: str, role: str = 'user'):
        if not isinstance(prompt, str):
            prompt = str(prompt)

        part = Part({'text': prompt})
        content = Content(role=role).add_part(part=part)
        self._prompt.add_content(content=content)

        content_len = len(Tokens(string=prompt))
        logger.debug(
            f"[GoogleGeminiClient] :: "
            f"add_content :: "
            f"{content_len:,} tokens ({len(self)} total) :: "
            f"{part.bytes}"
        )
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

        url = self._api.base.version(self.api_version).models(self.model).generateContent.key(
            key=self._config.random_api_key()).url
        json = self._prompt.to_prompt()
        chat = self._requests.post(url=url, json=json, headers=self._config.headers())

        if not chat:
            error = chat.to_dict().get('error')
            logger.error(f'[GoogleGeminiClient] :: chat :: ERROR :: {self.model} :: {error}')
            raise Exception(
                f'[GoogleGeminiClient] :: chat :: ERROR :: {self.model}',
                error,
                self.model
            )

        self._chat = GeminiResponse(chat.to_dict())

        if print_stream:
            self._chat.print_stream()

        self._prompt.add_content(self._chat.response.content)
        return self

    def chat_forever(self):

        def help():
            print(
                "USAGE:\n"
                "  /SEND\n"
                "  /EXIT\n"
                "  /HELP\n"
            )

        while True:
            prompt = ''
            lines = []

            print(f"INPUT (/SEND /EXIT /HELP): ")
            while True:
                try:
                    line = input()
                    line_stripped = line.strip().lower()

                    if line_stripped == '/send':
                        break

                    if line_stripped == '/exit':
                        logger.info(f"[GoogleGeminiClient] :: chat_forever :: done")
                        return self

                    if line_stripped == '/help':
                        help()
                        continue

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
        if self.api_version and self.model and self._config.is_ready():
            return True
        logger.error(f'[GoogleGeminiClient] :: is_ready :: ERROR')
        return False

    def set_model(self, model: Model, api_version: str):
        self.model = model.name
        self.api_version = api_version
        logger.debug(f"[GoogleGeminiClient] :: set_model:: {api_version} :: {model.name}")
        return self

    def set_random_model(self):
        if not self._models_search:
            self._find_model_all()

        models = []
        for api, models_ in self._models_search.items():
            for model in models_:
                if model.name_short in self._models.DONT_USE:
                    continue

                if model.name_short in self._models.NOT_GOOD:
                    continue

                if 'generateContent' in model.supportedGenerationMethods:
                    models.append((api, model))

        api, model = random.choice(models)
        return self.set_model(model=model, api_version=api)
