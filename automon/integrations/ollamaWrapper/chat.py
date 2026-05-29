import ollama

from automon.helpers.loggingWrapper import LoggingClient

from .tokens import Tokens
from ... import repr_str

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(LoggingClient.ERROR)


class OllamaChat(object):
    """Generator object returned from ollama.chat"""

    model: str
    _chat: ollama.chat

    def __init__(
            self,
            model: str,
            chat: ollama.chat,
    ):
        self.model = model
        self._chat = chat
        self._chunks = []
        self._consumed = False

    def __repr__(self):
        return repr_str([
            f'[OllamaChat]',
            f'{self.model}',
            f'{len(self._chunks)} chunks',
        ])

    def chunks(self):
        iterable = self._chunks if self._consumed else self._chat

        for chunk in iterable:
            if chunk not in self._chunks:
                self._chunks.append(chunk)
                yield chunk

        self._consumed = True

    def _content(self, message):
        return message.content

    def contents(self):
        for message in self._messages():
            yield self._content(message)

    def _message(self, chunk):
        return chunk.message

    def _messages(self):
        for chunk in self.chunks():
            yield self._message(chunk)

    def stream(self):
        for content in self.contents():
            print(content, end='', flush=True)
        return self

    def response(self) -> str:
        return ''.join(self.contents())

    def to_string(self) -> str:
        string = ''.join(self.contents())
        tokens = Tokens(string)
        logger.debug(f'[OllamaChat] :: to_string :: {tokens.count_pretty} tokens')
        return string
