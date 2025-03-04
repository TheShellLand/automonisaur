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

        self.chats: (OllamaChat) = ()

        self._ollama_chat: OllamaChat = None
        self._ollama_list = None

        self._safe_word = None
        self._chat_session = None
        self._chat_downloads = []

        self._full_chat_log = ''
        self._temp_dir = automon.helpers.tempfileWrapper.Tempfile.get_temp_dir()

        self._memory_usage_max = 0
        self._num_ctx = 9000

    @property
    def _ollama_options(self):
        return dict(
            num_ctx=self._num_ctx
        )

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
        return self

    def chat(self, show_profiler: bool = False, print_stream: bool = True, options: dict = None, **kwargs):
        """

        If you need an even larger context window, you can increase this to 131072 which is the 128k context limit that llama3.1 has.


        """
        if not options:
            options = self._ollama_options

        logger.debug(f'[OllamaClient] :: chat :: {options=} :: {sum_tokens(self.messages):,} total tokens >>>>')

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
            self._memory_alert_90()

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

        self.pickle_load()

        if not safe_word:
            safe_word = '/pineapples'
        self._safe_word = safe_word

        if system_content:
            self._agent_system_prompt(system_content=system_content)

        logger.debug(f'[OllamaClient] :: chat_forever :: {safe_word=}')
        print(
            f":: SYSTEM :: Remember to say your safe word and the chat experience will end. \n\n"
            f"Your safe word is: {safe_word}\n")

        while True:

            message = ''
            try:
                message += input(f"\n$> ")
                message = message.strip()
            except KeyboardInterrupt:
                self._agent_exit()
                break

            if not message:
                continue

            if message == self._safe_word:
                self._agent_exit()
                break

            if message == '/clear':
                self._agent_clear()
                continue

            if '/context' in message[:len('/context')]:
                self._agent_context(message=message)
                continue

            if message == '/downloads':
                self._agent_downloads()
                continue

            if '/download' in message[:len('/download')]:
                self._agent_download(message=message)
                continue

            if message == '/list':
                self._agent_list()
                continue

            if message == '/memory':
                self._agent_memory()
                continue

            if message == '/summary':
                self._agent_summary()
                continue

            if '/system' in message[:len('/system')]:
                system_content = message[len('/system'):]
                self._agent_system_prompt(system_content=system_content)
                continue

            if message == '/token':
                self._agent_token()
                continue

            if message == '/?':
                self._agent_help()
                continue

            if message not in self._full_chat_log:
                self._full_chat_log += message

            self.add_message(message).chat()
            self.pickle_save()

        logger.info(f'[OllamaClient] :: chat_forever :: done')

    @property
    def chat_response(self):
        try:
            return self.chats[-1].to_string()
        except:
            pass

    def _agent_clear(self):
        self.messages = [self.messages[0]]
        self._full_chat_log = ''
        print(f":: SYSTEM :: context memory cleared. ::")

    def _agent_context(self, message: str = None):
        if message:
            if 'set' in message:
                new_num_ctx = int(message.split(' ')[-1])

                if new_num_ctx > 0:
                    self._num_ctx = new_num_ctx

        print(f":: SYSTEM :: context window is at {self._num_ctx:,.0f} tokens ::")

    def _agent_download(self, message: str) -> tuple:
        logger.debug(f'[OllamaClient] :: _agent_download :: >>>>')

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
            download = automon.integrations.requestsWrapper.RequestsClient()
            download.get(url=url)
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
            if message not in self._full_chat_log:
                self._full_chat_log += message
                self.add_message(content=message)

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
        print(f":: SYSTEM :: Thank you for chatting. Shutting down. ::")

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

        for m in self.messages:
            role = m['role']
            content = m['content'].strip().splitlines()[0][:200]
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
            self.add_message(content=system_content, role='system')
            print(f":: SYSTEM :: new primary directive accepted. ::")
            return
        else:
            system_prompt = input(f"SYSTEM> ")

            if system_prompt:
                self.add_message(content=system_prompt, role='system')
                print(f":: SYSTEM :: new primary directive accepted. ::")
                return

        print(f":: SYSTEM :: proceeding with no primary directive. ::")

    def _agent_token(self):
        print(f":: SYSTEM :: message has {chr_to_tokens(self._full_chat_log):,} total tokens ::")

    def get_context_window(self):
        return self._num_ctx

    def get_total_tokens(self):
        return sum_tokens(self.messages)

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

    def _memory_alert_90(self):
        """Alert when memory usage over 90%"""
        percent = self._memory_watchdog().percent

        if percent > self._memory_usage_max:
            self._memory_usage_max = percent
            self._num_ctx *= 0.90
        else:
            self._num_ctx *= 1.10

        if percent > 90:
            return True

    def _memory_watchdog(self):
        """System memory stats"""
        # Get system memory information
        memory = psutil.virtual_memory()
        percent_used = memory.percent
        logger.debug(f'[OllamaClient] :: _memory_watchdog :: {percent_used=}')
        return memory

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

    def set_context_window(self, tokens: int):
        tokens = round(tokens)
        logger.debug(f'[OllamaClient] :: set_context_window :: {tokens=} :: >>>>')
        self._num_ctx = tokens
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
You are a chat bot talking to a person.
You will never make up an answer, if you don't have an answer just say you don't have an answer.
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
