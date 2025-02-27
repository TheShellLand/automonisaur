import ollama

from automon.helpers.loggingWrapper import LoggingClient

from .utils import chr_to_tokens

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(LoggingClient.ERROR)


class OllamaChat(object):
    """Generator object returned from ollama.chat"""

    def __init__(self, model: str, chat: ollama.chat, messages: list):
        self.model = model
        self.chat: ollama.chat = chat
        self.messages = messages

        self.chunks = []

    def __repr__(self):
        return f'[OllamaResponse]'

    def _chunk_content(self, chunk):
        content = self._chunk_message(chunk=chunk)['content']
        logger.debug(f'[OllamaChat] :: _chunk_content :: {chr_to_tokens(content)} tokens')
        return content

    def _chunk_message(self, chunk):
        return chunk['message']

    def content(self):
        return [message['content'] for message in self.message()]

    def _get_chunks(self):
        for chunk in self.chat:
            logger.debug(f'[OllamaChat] :: _get_chunks :: {chunk=}')
            self.chunks.append(chunk)
            yield chunk

    def message(self):
        return [chunk['message'] for chunk in self.chunks]

    def print_stream(self):
        try:
            for chunk in self._get_chunks():
                print(f'{self._chunk_content(chunk=chunk)}', end='', flush=True)

        except KeyboardInterrupt:
            print(f"\n:: SYSTEM :: ending transmission. ::")
            return self

        print('\n', flush=True)
        return self

    def to_string(self):
        if not self.chunks:
            self._get_chunks()

        string = ''.join(self.content())
        logger.debug(f'[OllamaChat] :: to_string :: {chr_to_tokens(string)} tokens')
        return string
