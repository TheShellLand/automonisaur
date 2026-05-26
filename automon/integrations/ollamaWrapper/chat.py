import ollama

from automon.helpers.loggingWrapper import LoggingClient

from .tokens import Tokens

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(LoggingClient.ERROR)


class OllamaChat(object):
    """Generator object returned from ollama.chat"""

    model: str
    _chat: ollama.chat

    chunks: list

    def __init__(
            self,
            model: str,
            chat: ollama.chat,
            messages: list
    ):
        self.model = model
        self._chat = chat

        self._chunks = []

    def __repr__(self):
        return f'[OllamaChat]'

    @property
    def chunks(self):
        for chunk in self._chat:
            if chunk not in self._chunks:
                self._chunks.append(chunk)
        return self._chunks

    @chunks.setter
    def chunks(self, chunks):
        self._chunks = chunks

    def _content(self, message):
        return message.content

    def contents(self) -> list:
        return [self._content(message) for message in self._messages()]

    def _message(self, chunk):
        return chunk.message

    def _messages(self) -> list:
        return [self._message(chunk) for chunk in self.chunks]

    def print_stream(self):
        response = ''.join(self.contents())
        print(f'{response}\n', flush=True)
        return self

    def response(self) -> str:
        return ''.join(self.contents())

    def to_string(self) -> str:
        string = ''.join(self.contents())
        tokens = Tokens(string)
        logger.debug(f'[OllamaChat] :: to_string :: {tokens.count_pretty} tokens')
        return string
