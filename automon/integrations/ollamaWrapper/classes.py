import ollama

from automon.helpers.loggingWrapper import LoggingClient

from .tokens import Tokens
from ... import repr_str

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(LoggingClient.ERROR)


class OllamaChat(object):
    """Generator object returned from ollama.chat"""

    model: str
    _chat: ollama.ChatResponse
    _chunks: list[ollama.ChatResponse]

    def __init__(
            self,
            model: str,
            chat: ollama.ChatResponse,
            stream: bool = None,
    ):
        self.model = model
        self._chat = chat
        self._chunks = []
        self._consumed = False
        self._stream = stream

    def __repr__(self):
        return repr_str([
            f'[OllamaChat]',
            f'{self.model}',
            f'{len(self._chunks)} chunks',
            f'{len(self._chunks)} tokens',
        ])

    def __len__(self):
        return sum([Tokens(x) for x in self.contents()])

    def chunks(self) -> ollama.ChatResponse:
        for chunk in self._chunks:
            yield chunk

        if not self._consumed:
            for chunk in self._chat:
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

    def print(self):
        return self.stream()

    def stream(self):
        for content in self.contents():
            print(content, end='', flush=True)
        print('\n', flush=True)
        return self

    def response(self) -> str:
        return self.to_string()

    def to_string(self) -> str:
        if not self._stream:
            return self._chat.message.content

        string = ''.join(self.contents())
        tokens = Tokens(string)
        logger.debug(f'[OllamaChat] :: to_string :: {tokens.count_pretty} tokens')
        return string
