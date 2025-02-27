import os
import ollama
import pickle
import automon
import hashlib
import cProfile
import datetime
import textwrap
import readline

import automon.helpers.tempfileWrapper
import automon.helpers.uuidWrapper
import automon.integrations.requestsWrapper

from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO, ERROR

from .chat import OllamaChat
from .utils import chr_to_tokens, sum_tokens

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

        self.chats = ()

        self._ollama_chat: OllamaChat = None
        self._ollama_list = None

        self._safe_word = None
        self._chat_session = None

        self._full_chat_log = ''
        self._temp_dir = automon.helpers.tempfileWrapper.Tempfile.get_temp_dir()

    def add_chain(self, content: str, delimiters: str = 'CHAT', **kwargs):
        logger.debug(f'[OllamaClient] :: add_chain >>>>')

        new_question = f'{content}'

        if self._ollama_chat:
            chat = self._ollama_chat.to_string()
            new_question = (
                f'{content}\n'
                f'<{delimiters}>{chat}</{delimiters}>'
            )

        self.add_message_followup(content=new_question, **kwargs)

        logger.info(f'[OllamaClient] :: add_chain :: done')
        return self

    def add_message(self, content: str, role: str = 'user'):
        logger.debug(
            f'[OllamaClient] :: '
            f'add_message :: '
            f'{role=} :: '
            f'{chr_to_tokens(content):,} tokens :: '
            f'{len(content)} chars :: >>>>')

        max_tokens = 128000
        if self.model == 'deepseek-r1:14b':
            max_tokens = 128000
            if chr_to_tokens(content) > max_tokens:
                logger.warning(
                    f'[OllamaClient] :: '
                    f'add_message :: '
                    f'too many tokens :: '
                    f'{chr_to_tokens(content):,} > 128k')

        message = {
            "role": role,
            "content": content
        }

        self.messages.append(message)

        total_tokens = sum_tokens(self.messages)

        logger.debug(
            f'[OllamaClient] :: '
            f'add_message :: '
            f'{total_tokens:,} of {max_tokens:,} tokens used :: '
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

    def clear_context(self):
        self.messages = []
        logger.info(f'[OllamaClient] :: clear_context :: done')
        print(f":: SYSTEM :: context memory cleared. ::")
        return self

    def chat(self, show_profiler: bool = False, print_stream: bool = True, options: dict = {'num_ctx': 9000}, **kwargs):
        """

        If you need an even larger context window, you can increase this to 131072 which is the 128k context limit that llama3.1 has.


        """
        logger.debug(f'[OllamaClient] :: chat :: {sum_tokens(self.messages):,} tokens >>>>')

        chat = ollama.chat(
            model=self.model,
            messages=self.messages,
            stream=self.STREAM,
            options=options,
            **kwargs
        )
        chat = OllamaChat(model=self.model, chat=chat, messages=self.messages)
        self.chats = self.chats + (chat,)
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

            if show_profiler:
                pr.print_stats(sort='cumulative')

        if time_delta:
            logger.debug(f'[OllamaClient] :: chat :: {chat=} :: {time_delta} runtime')
        logger.info(f'[OllamaClient] :: chat :: done')

        return self

    def chat_forever(self, safe_word: str = None, system_content: str = None):
        """Chat forever until you use your safe word. :) """
        logger.debug(f'[OllamaClient] :: chat_forever :: >>>>')

        downloads = []

        self.pickle_load()

        if not safe_word:
            safe_word = '/pineapples'
        self._safe_word = safe_word

        if system_content:
            self.add_message(content=system_content, role='system')
            print(f":: SYSTEM :: new primary directive accepted. ::")
        else:
            system_prompt = input(f"SYSTEM> ")

            if system_prompt:
                self.add_message(content=system_prompt, role='system')
                print(f":: SYSTEM :: new primary directive accepted. ::")

        logger.debug(f'[OllamaClient] :: chat_forever :: {safe_word=}')
        print(
            f":: SYSTEM :: Remember to say your safe word and the chat experience will end. \n\n"
            f"Your safe word is: {safe_word}\n")

        while True:

            message = ''
            message += input(f"\n$> ")

            if not message:
                continue

            if message == self._safe_word:
                print(f":: SYSTEM :: Thank you for chatting. Shutting down. ::")
                break

            if message == '/downloads':
                if not downloads:
                    print(f":: SYSTEM :: no downloads ::")
                    continue

                for d in downloads:
                    url = d['url']
                    hash = d['hash']
                    size = d['size']
                    print(f":: SYSTEM :: file {hash} {url} {size} ::")
                continue

            if '/download' in message[:len('/download')]:
                download = message[len('/download'):].strip()
                url = download
                hash = hashlib.md5(string=url.encode()).hexdigest()
                download = self._download(url=download)
                if download:
                    size = round(os.stat(os.path.join(self._temp_dir, hash)).st_size / 1024)
                    downloads.append(dict(url=url, hash=hash, size=f"{size:,} KB"))
                    message = f"Store this file: <{hash}>{download}</{hash}>"
                    if message not in self._full_chat_log:
                        self._full_chat_log += message
                        self.add_message(content=message)
                    continue
                continue

            if message == '/clear':
                self.messages = [self.messages[0]]
                self._full_chat_log = ''
                continue

            if message == '/list':
                if not self.messages:
                    print(f":: SYSTEM :: no messages ::")
                    continue
                for m in self.messages:
                    role = m['role']
                    content = m['content'].strip().splitlines()[0][:200]
                    print(f":: SYSTEM :: <{role}> {content}")
                continue

            if message == '/token':
                print(f":: SYSTEM :: message has {chr_to_tokens(self._full_chat_log):,} total tokens")
                continue

            if message not in self._full_chat_log:
                self._full_chat_log += message
            self.add_message(message).chat()
            self.pickle_save()

        logger.info(f'[OllamaClient] :: chat_forever :: done')

    def _download(self, url: str):
        logger.debug(f'[OllamaClient] :: _download :: >>>>')

        hash = hashlib.md5(string=url.encode()).hexdigest()
        tempfile = os.path.join(self._temp_dir, hash)

        download = None
        if os.path.exists(tempfile):
            filesize = os.stat(tempfile).st_size / 1024
            print(f":: SYSTEM :: existing file found {hash} {filesize:.2f} KB ::")
            with open(tempfile, 'r') as existing_file:
                download = existing_file.read()

        if not download:
            print(f":: SYSTEM :: downloading {url} ::")
            download = automon.integrations.requestsWrapper.RequestsClient()
            download.get(url=url)
            download = download.text

            if download:
                with open(tempfile, 'w') as new_file:
                    filesize = len(download) / 1024
                    print(f":: SYSTEM :: file saved {hash} {filesize:.2f} KB ::")
                    new_file.write(download)
            else:
                print(f":: SYSTEM :: nothing to download ::")

        logger.info(f'[OllamaClient] :: _download :: done')
        return download

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

    def pickle_load(self, session_name: str = None):

        chat_session = self._chat_session

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
        logger.info(f'[OllamaClient] :: pickle_load :: done')

    def pickle_save(self, session_name: str = None):

        if not session_name:
            session_name = automon.helpers.uuidWrapper.Uuid.hex()

        chat_session = self._chat_session

        if not chat_session:
            temp = automon.helpers.tempfileWrapper.Tempfile.get_temp_dir()
            chat_session = os.path.join(temp, session_name)

        with open(chat_session, 'wb') as session:
            pickle.dump(self.messages, session)

        logger.debug(
            f'[OllamaClient] :: pickle_save :: saved {chat_session=} :: {os.stat(chat_session).st_size / 1024:.2f} KB')
        logger.info(f'[OllamaClient] :: pickle_save :: done')

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

    def use_template_chatbot_with_thinking(self, content: str = ''):

        template = f"""
You are a senior python software engineer chat bot talking to a person.
You will always give short and direct answers. 
"""
        return template

    def use_template_chatbot_with_input(self, input: str, question: str):

        template = (f"""
You are a highly articulate and helpful chat bot. 
Your task is to answer questions using data provided in the <DATA> section.
    - Use the information in the <INPUT> section.

<INSTRUCTIONS>
-   Always give a truthful and honest answers.
-   You are allowed to ask a follow up question if it will help clarify the <INPUT> section.
-   For everything else, please explicitly mention these notes. 
-   Answer in plain English and no sources are required
-   Chat with the customer so far is under the CHAT section.
</INSTRUCTIONS>


QUESTION: {question}
ANSWER:


<DATA>
<INPUT>
{input}
</INPUT>
</DATA>

""")

        return self.add_chain(template)

    def use_template_chatbot_with_multi_input(self, input: [dict], question: str):
        """

        inputs: {
            "tag": "name of tag",
            "text" "string of text"
        }

        """

        INPUTS = []
        for input_ in input:
            tag = input_['tag']
            text = input_['text']

            INPUTS.append(f"<{tag}>\n{text}\n</{tag}>")

        INPUTS = '\n\n'.join(INPUTS)

        template = textwrap.dedent(f"""
You are a highly articulate and helpful chat bot. 
Your task is to answer questions using data provided in the <DATA> section.
    - Use the information in the <DATA> section.

<INSTRUCTIONS>
-   Always give a truthful and honest answers.
-   You are allowed to ask a follow up question if it will help clarify the <INPUT> section.
-   For everything else, please explicitly mention these notes. 
-   Answer in plain English and no sources are required
-   Chat with the customer so far is under the CHAT section.
</INSTRUCTIONS>


QUESTION: {question}
ANSWER:


<DATA>

{INPUTS}

</DATA>

""")
        return self.add_chain(template)
