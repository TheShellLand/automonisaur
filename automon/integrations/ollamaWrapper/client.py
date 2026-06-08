import os
import ollama
import psutil
import pickle
import hashlib
import cProfile
import datetime
import textwrap
import readline

import automon

import automon.helpers.uuidWrapper
import automon.helpers.tempfileWrapper

from automon.helpers import repr_str
from automon.helpers.debug import debug_exception
from automon.helpers.dictWrapper import DictHelper

from automon.integrations.requestsWrapper import RequestsClient
from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO, ERROR

from .classes import OllamaChat
from .utils import chr_to_tokens, sum_tokens
from .tokens import Tokens
from .prompt_templates import *

LoggingClient.logging.getLogger('httpcore.http11').setLevel(ERROR)
LoggingClient.logging.getLogger('httpcore.connection').setLevel(ERROR)

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


class OllamaOptions(DictHelper):
    """
    options={
        "temperature": 0.0,      # Eliminates randomness for strict adherence
        "top_p": 0.1,            # Locks the model into the highest probability tokens
        "num_predict": 1024      # Limits max output length to save processing time
        "num_ctx": 2048          # default 2048 tokens
    }

    """

    def __init__(
            self,
            temperature: float = None,
            top_p: float = None,
            num_predict: int = None,
            num_ctx: int = None,
    ):
        self.temperature = temperature
        self.top_p = top_p
        self.num_predict = num_predict
        self.num_ctx = num_ctx

        super().__init__()


class OllamaMessage(DictHelper):
    role: str
    content: str

    def __init__(self, message: dict):
        self.role = None
        self.content = None

        super().__init__(message)

    def __repr__(self):
        return repr_str([
            f'{self.role}',
            f'{self.content}',
        ])

    def __len__(self):
        return len(Tokens(self.content))


class OllamaClient:
    templates = Templates()

    model: str
    messages: list[dict]
    messages_pretty: list[OllamaMessage]

    _ollama: ollama.Client

    _max_tokens = {
        'deepseek-r1:14b': 128000,
        'gemma4:latest': 256000,
        'gemma4:12b': 256000,
    }

    def __init__(
            self,
            model: str = 'gemma4:latest',
            host: str = None
    ):
        self._ollama = ollama.Client(
            host=host,
        )

        self.model = model
        self.messages = []

        self._pickle_session = None
        self._chat_downloads = []

        self._temp_dir = automon.helpers.tempfileWrapper.Tempfile.get_temp_dir()

        self._memory_usage_max = 0
        self._num_ctx = 9000

    def _ollama_options(
            self,
            temperature: float = None,
            top_p: float = None,
            num_predict: int = None,
            num_ctx: int = None,
    ) -> OllamaOptions:

        return OllamaOptions(
            temperature=temperature,
            top_p=top_p,
            num_predict=num_predict,
            num_ctx=num_ctx,
        )

    def add_chain(self, content: str, **kwargs):
        raise debug_exception(locals(), f'depreciated: use OllamaClient.add_prompt instead')

    def add_system_prompt(self, content: str):
        return self.add_prompt(content=content, role='system')

    def add_prompt(self, content: str, role: str = AgentRole.USER):

        tokens = Tokens(content)

        logger.debug(
            f'[OllamaClient] :: '
            f'add_message :: '
            f'{role=} :: '
            f'{tokens.count_pretty} tokens :: '
            f'{len(content)} chars')

        message = {
            "role": role,
            "content": str(content)
        }

        self.messages.append(message)

        total_tokens = sum_tokens(self.messages_pretty)
        model = self.model
        max_tokens = self._max_tokens.get(model, 20000)

        if total_tokens > max_tokens:
            raise debug_exception(locals(), 'too many tokens')

        self.set_context_window(int(self.get_total_tokens() * 1.10))

        logger.debug(
            f'[OllamaClient] :: '
            f'add_message :: '
            f'{total_tokens:,} of {max_tokens:,} tokens used :: '
            f'{max_tokens - total_tokens:,} tokens remaining'
        )

        return self

    def clear_context(self):
        self.messages = []
        logger.info(f'[OllamaClient] :: clear_context :: done')
        return self

    def chat(
            self,
            print_stream: bool = True,
            options: OllamaOptions = None,
            **kwargs
    ) -> OllamaChat:
        """send prompt to model"""
        if options is None:
            options = self._ollama_options().to_dict()

        logger.debug(f'[OllamaClient] :: chat :: {options=} :: {sum_tokens(self.messages_pretty):,} total tokens')

        chat = self._ollama.chat(
            model=self.model,
            messages=self.messages,
            stream=print_stream,
            options=options,
            **kwargs
        )
        chat = OllamaChat(
            model=self.model,
            chat=chat,
            stream=print_stream
        )
        self._ollama_chat = chat

        if print_stream:
            chat.stream()

        self.add_prompt(content=chat.to_string(), role='assistant')

        return chat

    def chat_forever(self, system_content: str = None):

        self.pickle_load()

        if system_content:
            self._agent_system_prompt(system_content=system_content)

        while True:

            message = ''
            try:
                message += input(f"\n$> ")
                message = Markdown.lstrip(message)
            except KeyboardInterrupt:
                self._agent_exit()
                break

            if not message:
                continue

            if '/exit' in message.lower():
                self._agent_exit()
                return self

            if '/clear' in message.lower():
                self._agent_clear()
                continue

            if '/context' in message[:len('/context')]:
                self._agent_context(message=message)
                continue

            if '/downloads' in message.lower():
                self._agent_downloads()
                continue

            if '/download' in message[:len('/download')]:
                self._agent_download(message=message)
                continue

            if '/list' in message.lower():
                self._agent_list()
                continue

            if '/memory' in message.lower():
                self._agent_memory()
                continue

            if '/summary' in message.lower():
                self._agent_summary()
                continue

            if '/system' in message.lower()[:len('/system')]:
                system_content = message[len('/system'):]
                self._agent_system_prompt(system_content=system_content)
                continue

            if '/token' in message.lower():
                self._agent_token()
                continue

            if '/?' in message.lower():
                self._agent_help()
                continue

            self.add_prompt(message).chat()
            self.pickle_save()

        return

    @property
    def _chat_response(self) -> str | None:
        try:
            return self.messages_pretty[-1].content
        except:
            pass

    def _agent_clear(self):
        self.messages = []
        print(f":: SYSTEM :: context memory cleared. ::")

    def _agent_context(self, message: str = None):
        if message:
            if 'set' in message:
                new_num_ctx = int(message.split(' ')[-1])

                if new_num_ctx > 0:
                    self._num_ctx = new_num_ctx

        print(f":: SYSTEM :: context window is at {self._num_ctx:,.0f} tokens ::")

    def _agent_download(self, message: str) -> tuple:

        download = message[len('/download'):].strip()
        url = download

        hash = hashlib.sha1(string=url.encode()).hexdigest()[:7]
        pre = 'file-'
        ext = '.txt'
        filename = f"{pre}{hash}{ext}"

        tempfile = os.path.join(self._temp_dir, filename)

        download = None
        if os.path.exists(tempfile):
            filesize = os.stat(tempfile).st_size / 1024
            print(f":: SYSTEM :: existing file found {filename} {filesize:.2f} KB ::")
            with open(tempfile, 'r') as existing_file:
                download = existing_file.read()

        if not download:
            print(f":: SYSTEM :: downloading {url} ::")
            download = RequestsClient(url=url).get()
            download = download.text

        if download:
            with open(tempfile, 'w') as new_file:
                filesize = len(download) / 1024
                print(f":: SYSTEM :: downloaded file saved {filename} {filesize:.2f} KB ::")
                new_file.write(download)
        else:
            print(f":: SYSTEM :: nothing to download ::")

        if download:
            file_size = os.stat(os.path.join(self._temp_dir, filename)).st_size
            size = round(file_size / 1024)
            self._chat_downloads.append(dict(url=url, filename=filename, size=f"{size:,} KB"))
            message = f"This is the contents of a file: <{filename}>{download}</{filename}>"
            self.add_prompt(content=message)

        logger.info(f'[OllamaClient] :: _download :: done')
        return download, filename

    def _agent_downloads(self):
        if not self._chat_downloads:
            print(f":: SYSTEM :: no downloads ::")
            return

        for d in self._chat_downloads:
            url = d['url']
            filename = d['filename']
            size = d['size']
            print(f":: SYSTEM :: downloaded file {filename} {url} {size} ::")

    def _agent_exit(self):
        print(f":: SYSTEM :: Thank you for chatting. Terminating. ::")

    def _agent_help(self):
        print(f":: {'COMMANDS':20} {'':<30} ::")
        print(f':: {"":20} {"":<30} ::')
        print(f":: {'/clear':20} {'clear context window.':<30} ::")
        print(f":: {'/context':20} {'show context window.':<30} ::")
        print(f":: {'/context set <int>':20} {'set context window size.':<30} ::")
        print(f":: {'/download <url>':20} {'download url.':<30} ::")
        print(f":: {'/list <url>':20} {'list context window.':<30} ::")
        print(f":: {'/memory <url>':20} {'show memory usage.':<30} ::")
        print(f":: {'/summary <url>':20} {'show summary.':<30} ::")
        print(f":: {'/system <content>':20} {'set a new system directive.':<30} ::")
        print(f":: {'/token':20} {'show total tokens.':<30} ::")

    def _agent_list(self):
        if not self.messages:
            print(f":: SYSTEM :: no messages ::")
            return

        for message in self.messages_pretty:
            role = message.role
            content = message.content.splitlines[0][:200]
            print(f":: SYSTEM :: <{role}> {content} ::")

    def _agent_memory(self):
        print(f":: SYSTEM :: max memory usage was {self._memory_usage_max}% ::")

    def _agent_summary(self):
        self._agent_list()
        print()
        self._agent_downloads()
        print()
        self._agent_context()
        print()
        self._agent_token()
        print()
        self._agent_memory()
        print()

    def _agent_system_prompt(self, system_content: str):
        if system_content:
            system_content = system_content.strip()
            self.add_prompt(content=system_content, role='system')
            print(f":: SYSTEM :: new primary directive accepted. ::")
            return
        else:
            system_prompt = input(f"SYSTEM> ")

            if system_prompt:
                self.add_prompt(content=system_prompt, role='system')
                print(f":: SYSTEM :: new primary directive accepted. ::")
                return

        print(f":: SYSTEM :: proceeding with no primary directive. ::")

    def _agent_token(self):
        print(f":: SYSTEM :: message has {sum(self.messages_pretty)} total tokens ::")

    def get_context_window(self):
        return self._num_ctx

    def get_total_tokens(self) -> int:
        return sum_tokens(self.messages_pretty)

    def has_downloaded_models(self, model: str):

        for model_ in self.list_models():
            if model == model_.model:
                return True
        return False

    def is_ready(self):

        try:
            if not self.start_local_server():
                return False

            if self.has_downloaded_models(self.model):
                return True
        except Exception as error:
            raise debug_exception(locals(), error)

        return False

    def list(self):
        return self._ollama.list()

    def list_models(self):
        return self.list().models

    @property
    def messages_pretty(self):
        return [OllamaMessage(x) for x in self.messages]

    def _memory_alert_90(self) -> bool:
        """Alert when memory usage over 90%"""
        percent = self._memory_watchdog().percent

        if percent > self._memory_usage_max:
            self._memory_usage_max = percent
            self._num_ctx *= 0.90
        else:
            self._num_ctx *= 1.10

        if percent > 90:
            return True
        return False

    def _memory_watchdog(self):
        """System memory stats"""
        # Get system memory information
        memory = psutil.virtual_memory()
        percent_used = memory.percent
        logger.debug(f'[OllamaClient] :: _memory_watchdog :: {percent_used=}')
        return memory

    def pickle_load(self, session_name: str = None):

        chat_session = self._pickle_session

        if session_name:
            temp = automon.helpers.tempfileWrapper.Tempfile.get_temp_dir()
            session_search = os.path.join(temp, session_name) + '.pickle'
            if os.path.exists(session_search):
                chat_session = session_search

        if not chat_session:
            logger.debug(f'[OllamaClient] :: pickle_load :: no session found :: {chat_session=}')
            return False

        with open(chat_session, 'rb') as session:
            self.messages = pickle.load(session)

        logger.debug(
            f'[OllamaClient] :: pickle_load :: {chat_session=} :: {os.stat(chat_session).st_size / 1024:.2f} KB')

    def pickle_save(self, session_name: str = None):

        if not session_name:
            session_name = automon.helpers.uuidWrapper.Uuid.hex()

        chat_session = self._pickle_session

        if not chat_session:
            temp = automon.helpers.tempfileWrapper.Tempfile.get_temp_dir()
            chat_session = os.path.join(temp, session_name)

        with open(chat_session, 'wb') as session:
            pickle.dump(self.messages, session)

        logger.debug(
            f'[OllamaClient] :: pickle_save :: saved {chat_session=} :: {os.stat(chat_session).st_size / 1024:.2f} KB')

    def _pull_model(self, model: str):
        return self._ollama.pull(model=model)

    def pull_model(self, model: str):
        if self._pull_model(model).status == 'success':
            return True
        return False

    def response(self):
        return self.messages_pretty[-1]

    def set_context_window(self, tokens: int):
        tokens = round(tokens)
        logger.debug(f'[OllamaClient] :: set_context_window :: {tokens=}')
        self._num_ctx = tokens
        return self

    def set_model(self, model: str):
        logger.debug(f'[OllamaClient] :: set_model :: {model=}')
        self.model = model
        return self

    @staticmethod
    def start_local_server() -> bool:
        try:
            ollama = automon.helpers.subprocessWrapper.Run('ollama list')

            if ollama.returncode == 0:
                logger.debug(f'[OllamaClient] :: start_local_server :: {ollama.stdout}')
                return True

        except Exception as error:
            logger.error(f'[OllamaClient] :: start_local_server :: {error}')

        logger.error(f'[OllamaClient] :: start_local_server :: failed')
        return False
