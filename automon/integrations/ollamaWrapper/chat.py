import ollama

from automon.helpers.loggingWrapper import LoggingClient

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(LoggingClient.DEBUG)


class OllamaChat(object):
    """Generator object returned from ollama.chat"""

    def __init__(self, model: str, chat: ollama.chat):
        self.model = model
        self.chat: ollama.chat = chat

        self.chunks = []

    def __repr__(self):
        return f'[OllamaResponse]'

    def _chunk_content(self, chunk):
        content = self._chunk_message(chunk=chunk)['content']
        logger.debug(f'[OllamaChat] :: _chunk_content :: {len(content)} tokens')
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
        for chunk in self._get_chunks():
            print(f'{self._chunk_content(chunk=chunk)}', end='', flush=True)
        print('\n\n', flush=True)
        return self

    def to_string(self):
        if not self.chunks:
            self._get_chunks()

        string = ''.join(self.content())
        logger.debug(f'[OllamaChat] :: to_string :: {len(string)} tokens')
        return string
