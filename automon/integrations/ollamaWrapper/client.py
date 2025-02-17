import automon
import ollama

from automon.helpers.loggingWrapper import LoggingClient

LoggingClient.logging.getLogger('httpcore.http11').setLevel(LoggingClient.ERROR)
LoggingClient.logging.getLogger('httpcore.connection').setLevel(LoggingClient.ERROR)

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(LoggingClient.DEBUG)


class OllamaResponse(object):
    """Generator object returned from ollama.chat"""

    def __init__(self, model: str, response: ollama.chat):
        self._response: ollama.chat = response
        self.chunks = []

        self._chunks()

    def __repr__(self):
        return f'[OllamaResponse]'

    def _chunks(self):
        for chunk in self._response:
            self.chunks.append(chunk)

    def content(self):
        return [message['content'] for message in self.message()]

    def message(self):
        return [chunk['message'] for chunk in self.chunks]

    def to_string(self):
        return ''.join(self.content())


class OllamaClient(object):

    def __init__(self, model: str = 'deepseek-r1:14b', messages: list = [], stream: bool = True):
        self.ollama: ollama = ollama
        self.model: str = model
        self.messages: list = messages
        self.STREAM: ollama.chat = stream

        self.response: OllamaResponse = None
        self._list = None

    def add_message(self, content: str, role: str = 'user'):
        logger.debug(f'[OllamaClient] :: add_message :: {role=} :: {len(content):,} tokens >>>>')

        if self.model == 'deepseek-r1:14b':
            if len(content) > 128000:
                logger.warning(f'[OllamaClient] :: add_message :: too many tokens :: {len(content):,} > 128k')

        message = {
            "role": role,
            "content": content
        }

        self.messages.append(message)

        logger.debug(
            f'[OllamaClient] :: '
            f'add_message :: '
            f'{sum(len(s["content"]) for s in self.messages):,} total tokens'
        )
        logger.info(f'[OllamaClient] :: add_message :: done')

        return self

    def chat(self, show_profiler: bool = False, **kwargs):
        logger.debug(f'[OllamaClient] :: chat :: {sum(len(s["content"]) for s in self.messages):,} tokens >>>>')

        import cProfile

        pr = cProfile.Profile()
        pr.enable()

        response = ollama.chat(
            model=self.model,
            messages=self.messages,
            stream=self.STREAM,
            **kwargs
        )
        response = OllamaResponse(model=self.model, response=response)
        self.response = response

        logger.debug(f'[OllamaClient] :: chat :: {response=}')
        logger.info(f'[OllamaClient] :: chat :: done')

        pr.disable()

        if show_profiler:
            pr.print_stats(sort='cumulative')

        return self

    def has_downloaded_models(self):
        self.list()

        if self._list:
            return True

        return False

    def is_ready(self):
        logger.debug(f'[OllamaClient] :: is_ready :: >>>>')

        try:
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

        self._list = list

        logger.debug(f'[OllamaClient] :: list :: {len(models)} model(s)')
        logger.info(f'[OllamaClient] :: list :: done')
        return self

    def pull(self, model: str = 'deepseek-r1:14b'):
        logger.debug(f'[OllamaClient] :: pull :: {model=} :: >>>>')

        pull = self.ollama.pull(model=model)

        logger.debug(f'[OllamaClient] :: pull :: {pull=}')
        logger.info(f'[OllamaClient] :: pull :: done')
        return self

    def print_response(self):
        logger.debug(f'[OllamaClient] :: print_response :: >>>>')

        for content in self.response.content():
            # logger.debug(f'[OllamaClient] :: print_response :: {content=}')
            print(content, end='', flush=True)
        print()

        logger.info(f'[OllamaClient] :: print_response :: done')
        return self
