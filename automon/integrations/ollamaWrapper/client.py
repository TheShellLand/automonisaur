import automon
import ollama
import cProfile
import datetime

from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO, ERROR

from .chat import OllamaChat

LoggingClient.logging.getLogger('httpcore.http11').setLevel(ERROR)
LoggingClient.logging.getLogger('httpcore.connection').setLevel(ERROR)

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


class OllamaClient(object):

    def __init__(self, model: str = 'deepseek-r1:14b', messages: list = [], stream: bool = True):
        self.ollama: ollama = ollama
        self.model: str = model
        self.messages: list = messages
        self.STREAM: ollama.chat = stream

        self._ollama_chat: OllamaChat = None
        self._ollama_list = None

    def add_chain(self, content: str, **kwargs):
        logger.debug(f'[OllamaClient] :: add_chain >>>>')

        new_question = f'{content}'

        if self._ollama_chat:
            answer = self._ollama_chat.to_string()
            new_question = f'{content}\n\n{answer}'

        self.add_message_followup(content=new_question, **kwargs)

        logger.info(f'[OllamaClient] :: add_chain :: done')
        return self

    def add_message(self, content: str, role: str = 'user'):
        logger.debug(f'[OllamaClient] :: add_message :: {role=} :: {len(content):,} tokens >>>>')

        max_tokens = 128000
        if self.model == 'deepseek-r1:14b':
            max_tokens = 128000
            if len(content) > max_tokens:
                logger.warning(f'[OllamaClient] :: add_message :: too many tokens :: {len(content):,} > 128k')

        message = {
            "role": role,
            "content": content
        }

        self.messages.append(message)

        total_tokens = sum(len(s["content"]) for s in self.messages)

        logger.debug(
            f'[OllamaClient] :: '
            f'add_message :: '
            f'{total_tokens:,} / {max_tokens:,} tokens used :: '
            f'{max_tokens - total_tokens:,} tokens remaining'
        )
        logger.info(f'[OllamaClient] :: add_message :: done')

        return self

    def add_message_followup(self, **kwargs):
        logger.debug(f'[OllamaClient] :: add_message_followup >>>>')
        self.messages = []
        self.add_message(**kwargs)
        logger.info(f'[OllamaClient] :: add_message_followup :: done')

        return self

    def chat(self, show_profiler: bool = False, print_stream: bool = True, **kwargs):
        logger.debug(f'[OllamaClient] :: chat :: {sum(len(s["content"]) for s in self.messages):,} tokens >>>>')

        chat = ollama.chat(
            model=self.model,
            messages=self.messages,
            stream=self.STREAM,
            **kwargs
        )
        chat = OllamaChat(model=self.model, chat=chat)
        self._ollama_chat = chat

        time_delta = None
        if print_stream:
            pr = cProfile.Profile()
            time_start = datetime.datetime.now()
            pr.enable()

            chat.print_stream()

            pr.disable()
            time_stop = datetime.datetime.now()
            time_delta = time_stop - time_start
            time_delta = datetime.timedelta(seconds=time_delta.seconds)

        if time_delta:
            logger.debug(f'[OllamaClient] :: chat :: {chat=} :: {time_delta} runtime')
        logger.info(f'[OllamaClient] :: chat :: done')

        if show_profiler:
            pr.print_stats(sort='cumulative')

        return self

    def has_downloaded_models(self):
        self.list()

        if self._ollama_list:
            return True

        return False

    def is_ready(self):
        logger.debug(f'[OllamaClient] :: is_ready :: >>>>')

        try:
            if not self.start_local_server():
                return False

            if self.has_downloaded_models():
                logger.info(f'[OllamaClient] :: is_ready :: done')
                return True
        except Exception as error:
            logger.error(f'[OllamaClient] :: is_ready :: ERROR :: {error=}')

        logger.info(f'[OllamaClient] :: is_ready :: done')
        return False

    def list(self):
        logger.debug(f'[OllamaClient] :: list :: >>>>')

        list = self.ollama.list()
        models = list['models']

        if models:
            for model in models:
                logger.debug(f'[OllamaClient] :: list :: {model=}')

        self._ollama_list = list

        logger.debug(f'[OllamaClient] :: list :: {len(models)} model(s)')
        logger.info(f'[OllamaClient] :: list :: done')
        return self

    @staticmethod
    def start_local_server() -> bool:
        logger.debug(f'[OllamaClient] :: start_local_server >>>>')

        try:
            ollama = automon.helpers.subprocessWrapper.Run('ollama list')

            if ollama.returncode == 0:
                logger.debug(f'[OllamaClient] :: start_local_server :: {ollama.stdout}')
                return True

        except Exception as error:
            raise Exception(f'[OllamaClient] :: start_local_server :: ERROR :: {error=}')

        logger.info(f'[OllamaClient] :: start_local_server :: failed')
        return False

    def pull(self, model: str = 'deepseek-r1:14b'):
        logger.debug(f'[OllamaClient] :: pull :: {model=} :: >>>>')

        pull = self.ollama.pull(model=model)

        logger.debug(f'[OllamaClient] :: pull :: {pull=}')
        logger.info(f'[OllamaClient] :: pull :: done')
        return self

    def print_response(self):
        logger.debug(f'[OllamaClient] :: print_response :: >>>>')

        if not self._ollama_chat.content():
            return self

        for content in self._ollama_chat.content():
            # logger.debug(f'[OllamaClient] :: print_response :: {content=}')
            print(content, end='', flush=True)

        logger.info(f'[OllamaClient] :: print_response :: done')
        return self
