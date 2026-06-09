import ollama

from datetime import timedelta
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

        load_time = self._load_time

        read_time = self._read_time
        read_tokens = self._read_tokens

        think_time = self._think_time
        think_tokens = self._think_tokens

        total_time = self._total_time
        total_time_s = self._total_time_seconds
        total_tokens = self._total_tokens

        write_tokens = len(self)

        done_reason = self._done_reason

        return repr_str([
            f'{self.model}',
            f'{write_tokens} tokens',
            f'{total_tokens / total_time_s :,.0f} T/s',
            f'total ({total_time}/{total_tokens:,} T)',
            f'read ({read_time}/{read_tokens:,} T)',
            f'think ({think_time}/{think_tokens:,} T)',
            f'load ({load_time})',
            f'{len(self._chunks)} chunks',
            f'{done_reason=}',
        ])

    def __len__(self):
        return sum([len(Tokens(x)) for x in self.contents()])

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

    def _to_seconds(self, nanoseconds: int) -> float | None:
        if nanoseconds is not None:
            return nanoseconds / 1_000_000_000

    def _to_seconds_str(self, nanoseconds: int) -> str | None:
        if nanoseconds is not None:
            return f'{self._to_seconds(nanoseconds):.2f}s'

    def _to_human_time(self, nanoseconds: int) -> timedelta | None:
        if nanoseconds is not None:
            return timedelta(nanoseconds=nanoseconds)

    @property
    def _load_time(self) -> str:
        return self._to_seconds_str(self._load_duration)

    @property
    def _read_time(self) -> str:
        self._to_seconds_str(self._prompt_eval_duration)

    @property
    def _read_tokens(self) -> int:
        return self._prompt_eval_count

    @property
    def _think_time(self) -> str:
        return self._to_seconds_str(self._eval_duration)

    @property
    def _think_tokens(self) -> int:
        return self._eval_count

    @property
    def _total_time(self) -> str:
        return self._to_seconds_str(self._total_duration)

    @property
    def _total_time_seconds(self) -> int:
        return self._to_seconds(self._total_duration)

    @property
    def _done(self) -> bool:
        if self._chunks:
            return self._chunks[-1].done

    @property
    def _done_reason(self) -> str:
        """The reason the generation finished (e.g., 'stop', 'length')."""
        if self._chunks:
            return self._chunks[-1].done_reason

    @property
    def _eval_count(self) -> int:
        """The number of tokens evaluated during the generation phase.
        Only the new words/tokens the AI created for you.
        """
        if self._chunks:
            return self._chunks[-1].eval_count

    @property
    def _eval_duration(self) -> int:
        """The duration of evaluation in nanoseconds.
        How fast is the model generating new text
        """
        if self._chunks:
            return self._chunks[-1].eval_duration

    @property
    def _load_duration(self) -> int:
        """The time taken to load the model into memory, in nanoseconds."""
        if self._chunks:
            return self._chunks[-1].load_duration

    @property
    def _prompt_eval_count(self) -> int:
        """The number of tokens evaluated in the initial prompt.
        System prompts, history, and your current question.
        """
        if self._chunks:
            return self._chunks[-1].prompt_eval_count

    @property
    def _prompt_eval_duration(self) -> int:
        """The duration spent evaluating the input prompt, in nanoseconds.
        How fast did the system ingest my input
        """
        if self._chunks:
            return self._chunks[-1].prompt_eval_duration

    @property
    def _total_duration(self) -> int:
        """The total request time (prompt + generation) in nanoseconds."""
        if self._chunks:
            return self._chunks[-1].total_duration

    @property
    def _total_tokens(self) -> int:
        if all([self._prompt_eval_count is not None, self._eval_count is not None]):
            return sum([self._prompt_eval_count, self._eval_count])
        return 0
