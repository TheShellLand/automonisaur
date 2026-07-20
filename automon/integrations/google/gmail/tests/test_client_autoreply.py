import unittest

import time
import random

from queue import Queue

from automon.helpers import *
from automon.integrations.ollamaWrapper import *
from automon.helpers.threadingWrapper import ThreadingClient
from automon.integrations.google.gmail import *
from automon.integrations.ollamaWrapper import OllamaClient, Markdown
from automon.integrations.google.gemini import GoogleGeminiClient
from automon import LoggingClient, ERROR, DEBUG, CRITICAL, INFO, debug

"""

queues

"""

queue_threads: Queue[GmailThread] = Queue(maxsize=5)
queue_new: Queue[GmailThread] = Queue(maxsize=5)
queue_send: Queue[tuple[GmailThread, GmailDraft, OllamaClient]] = Queue()
queue_skipped: Queue[GmailThread] = Queue()
queue_followup: Queue[GmailThread] = Queue()
queue_sent: Queue[GmailThread] = Queue()
queue_waiting: Queue[GmailThread] = Queue()
queue_analyze: Queue[GmailThread] = Queue()
queue_waiting_for_first_call: Queue[GmailThread] = Queue()
queue_waiting_for_interview: Queue[GmailThread] = Queue()

queue_unknown: Queue[GmailThread] = Queue()

queue_error: Queue[GmailThread] = Queue()
queue_log: Queue[tuple[str, int]] = Queue()

queue_tokens: Queue[int] = Queue()

queues = [
    queue_threads,
    queue_new,
    queue_send,
    queue_skipped,
    queue_followup,
    queue_analyze,
    queue_waiting,
    queue_sent,
    queue_waiting_for_first_call,
    queue_waiting_for_interview,
    queue_unknown,
    queue_error,
    queue_log,
    queue_tokens,
]

"""

logging settings

"""

DEBUG_LEVEL = 2
DEBUG_ = False
DEFAULT_LEVEL = DEBUG

LoggingClient.logging.getLogger('httpx').setLevel(DEFAULT_LEVEL)
LoggingClient.logging.getLogger('httpcore').setLevel(DEFAULT_LEVEL)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.client').setLevel(DEFAULT_LEVEL)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.utils').setLevel(DEFAULT_LEVEL)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.chat').setLevel(DEFAULT_LEVEL)
LoggingClient.logging.getLogger('automon.integrations.requestsWrapper.client').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.google.oauth.config').setLevel(DEFAULT_LEVEL)
LoggingClient.logging.getLogger('automon.integrations.google.gemini.api').setLevel(DEFAULT_LEVEL)
LoggingClient.logging.getLogger('automon.integrations.google.gemini.config').setLevel(DEFAULT_LEVEL)
LoggingClient.logging.getLogger('automon.integrations.google.gemini.client').setLevel(DEFAULT_LEVEL)
LoggingClient.logging.getLogger('automon.integrations.google.gmail.client').setLevel(DEFAULT_LEVEL)
LoggingClient.logging.getLogger('opentelemetry.instrumentation.instrumentor').setLevel(DEFAULT_LEVEL)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.tokens').setLevel(DEFAULT_LEVEL)
LoggingClient.logging.getLogger('automon.helpers.threadingWrapper.client').setLevel(DEFAULT_LEVEL)

if DEBUG_:
    LoggingClient.logging.getLogger('automon.integrations.google.gemini.client').setLevel(DEBUG)
    LoggingClient.logging.getLogger('automon.integrations.google.gmail.client').setLevel(DEBUG)
else:
    LoggingClient.logging.getLogger('automon.integrations.google.gemini.client').setLevel(INFO)
    LoggingClient.logging.getLogger('automon.integrations.google.gmail.client').setLevel(ERROR)

"""

llm settings

"""

USE_OLLAMA = True
USE_GEMINI = False
CHAT_FOREVER = False
CHAT_STREAM = True

OLLAMA_MODEL = 'gemma4:12b'
OLLAMA_HOST_GPU_5070fe = 'http://100.116.243.98:11434'
OLLAMA_HOST_GPU_1080ti = 'http://100.120.42.82:11434'

OLLAMA_HOSTS = [
    OLLAMA_HOST_GPU_1080ti,
    # None,
]


def random_ollama_host():
    return random.choice(OLLAMA_HOSTS)


gemini = GoogleGeminiClient()

TOTAL_TOKENS = 0

"""

gmail settings

"""

gmail = AutomonGmailClient()

# gmail.config.add_gmail_scopes()
gmail.config.add_scopes([
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
])

labels = gmail._labels
RESUME: GmailThread = None
RESUME_ATTACHMENT = None


def gmail_token_refresher(gmail: AutomonGmailClient):
    while True:
        try:
            if gmail.config.refresh_token():
                queue_log.put((f'[gmail_token_refresher] :: refreshed', 1))
                time.sleep(60 * 5)
        except Exception as error:
            queue_log.put((f'[gmail_token_refresher] :: ERROR :: {error=}', 1))

        time.sleep(60)


def automon_init(client: AutomonGmailClient):
    pass


def get_threads(gmail: AutomonGmailClient):
    while True:

        while not gmail.is_ready():
            time.sleep(0.1)

        try:
            query_sequence = [
                [labels.automon, labels.error],
                [labels.automon, labels.processing],
                [labels.automon, labels.followup],
                [labels.automon, labels.analyze],
                [labels.automon, labels.waiting],
                [labels.automon],
            ]

            nextPageToken = None

            for query in query_sequence:
                thread_search = gmail.thread_list_automon(
                    # maxResults=1,
                    pageToken=nextPageToken,
                    labelIds=query,
                )
                queue_log.put((f'[get_threads] :: {query} :: {thread_search}', 3))

                for thread in thread_search.threads:
                    queue_threads.put(thread)
                    queue_log.put((f'[get_threads] :: {queue_threads.qsize()} processed', 3))

                nextPageToken = thread_search.nextPageToken

            time.sleep(0.1)

        except Exception as error:
            queue_log.put((f'[get_threads] :: ERROR :: {error=}', 1))
            time.sleep(60)


def get_resume(gmail: AutomonGmailClient):
    global RESUME
    global RESUME_ATTACHMENT

    while not gmail.is_ready():
        time.sleep(0.1)

    while RESUME is None:
        threads = gmail.thread_list_automon(
            maxResults=1,
            labelIds=[labels.automon, labels.resume]
        )

        for thread in threads.threads:
            if gmail.is_resume(thread):
                RESUME = thread
                RESUME_ATTACHMENT = thread._message_first.find_attachment_pdf()
                queue_log.put((f'[get_resume] :: {thread} :: {RESUME}', 3))


def processor_email_thread(gmail: AutomonGmailClient):
    while True:

        while not gmail.is_ready():
            time.sleep(0.1)

        thread = queue_threads.get()

        try:
            queue_log.put((f'[processor_email_thread] :: {thread}', 3))

            # resume
            if gmail.is_resume(thread):
                queue_threads.task_done()
                continue

            gmail.clean_drafts(thread)

            # skipped
            if gmail.is_skipped(thread):
                queue_skipped.put(thread)
                queue_threads.task_done()
                queue_log.put((f'[processor_email_thread] :: queue_skipped :: {queue_skipped.qsize()} threads', 2))
                continue

            # error
            if gmail.is_error(thread):
                queue_error.put(thread)
                queue_threads.task_done()
                queue_log.put((f'[processor_email_thread] :: queue_error :: {queue_error.qsize()} threads', 2))
                continue

            # analyze
            if gmail.is_analyze(thread):
                queue_analyze.put(thread)
                queue_threads.task_done()
                queue_log.put((f'[processor_email_thread] :: queue_analyze :: {queue_analyze.qsize()} threads', 2))
                continue

            # scheduled
            if gmail.is_scheduled(thread):
                pass

            # new
            if gmail.is_new(thread):
                queue_new.put(thread)
                queue_threads.task_done()
                continue

            # followup
            if gmail.is_follow_up(thread):
                queue_followup.put(thread)
                queue_threads.task_done()
                continue

            # sent
            if gmail.is_sent(thread):
                thread = gmail.thread_get_automon(id=thread.id)

                queue_sent.put(thread)
                queue_threads.task_done()
                continue

            queue_unknown.put(thread)
            queue_log.put(
                (f'[processor_email_thread] :: queue_unknown :: {queue_unknown.qsize()} threads :: {thread}', 2))

            gmail.messages_modify_automon(
                id=thread._message_first.id,
                removeLabelIds=[labels.processing])

            queue_threads.task_done()
            time.sleep(0.1)

        except Exception as error:
            # queue_threads.put(thread)
            queue_log.put((f'[processor_email_thread] :: ERROR :: {error=}', 1))
            time.sleep(60)


def processor_email_new(gmail: AutomonGmailClient):
    global RESUME

    _PROCESSING = True
    while _PROCESSING:

        while not gmail.is_ready():
            time.sleep(0.1)

        while RESUME is None:
            time.sleep(5)

        thread: GmailThread = queue_new.get()

        try:
            queue_log.put((f'[processor_email_new] :: {thread}', 2))

            gmail.messages_modify_automon(
                id=thread._message_first.id,
                addLabelIds=[labels.processing])

            resume_str = RESUME._message_first._attachments_first.body._data_html_text
            identity = RESUME._message_first._email_from
            background = resume_str

            resume_prompt = OllamaClient.templates.markdown.str_to_markdown(
                header='resume',
                header_level=1,
                text=resume_str,
            )

            human = HumanAgent(
                name=identity,
                memory=background,
            )

            response_passed = False
            response = False
            exit_loop = False
            while not response_passed or not exit_loop:

                try:
                    # if not is_job_email(thread):
                    #     gmail.thread_modify(id=thread.id, addLabelIds=[labels.unread, labels.skipped])
                    #     exit_loop = True
                    #     break

                    # if is_rejected_email(thread):
                    #     gmail.thread_modify(id=thread.id, addLabelIds=[labels.unread, labels.skipped])
                    #     exit_loop = True
                    #     break

                    response, ollama = write_email_reply(identity=human, thread=thread)
                    if is_good_reply(response=response):
                        response_passed = True
                        exit_loop = True
                        break


                except Exception as error:
                    ollama = OllamaClient(host=random_ollama_host()).set_model(OLLAMA_MODEL)
                    ollama.add_system_prompt(human)
                    ollama.add_prompt(thread.to_prompt())
                    ollama.chat_forever()
                    raise debug_exception(locals(), error)

            if response_passed:
                if not gmail.is_skipped(thread):
                    draft = None

                    if gmail.is_new(thread):
                        resume_attachment = RESUME_ATTACHMENT

                        draft = draft_create(
                            thread=thread,
                            response=response,
                            resume_attachment=resume_attachment,
                        )

                    if draft is not None:
                        if labels.auto_reply in thread._messages_labels:
                            queue_send.put((thread, draft, ollama))

                            gmail.messages_modify_automon(
                                id=thread._message_first.id,
                                removeLabelIds=[labels.processing],
                            )

            queue_new.task_done()

        except Exception as error:
            # queue_new.put(thread)
            queue_log.put((f'[processor_email_new] :: ERROR :: {error=}', 1))
            time.sleep(60)


def processor_email_sent(gmail: AutomonGmailClient):
    while True:

        while not gmail.is_ready():
            time.sleep(0.1)

        thread = queue_sent.get()

        try:
            queue_log.put((f'[processor_email_sent] :: {queue_sent.qsize()} left :: {thread}', 2))

            if gmail.is_old(thread):
                queue_followup.put(thread)
                queue_sent.task_done()
                continue

            queue_waiting.put(thread)
            queue_sent.task_done()

        except Exception as error:
            # queue_sent.put(thread)
            queue_log.put((f'[processor_email_sent] :: ERROR :: {error=}', 1))
            time.sleep(60)


def processor_draft_send(gmail: AutomonGmailClient):
    while True:

        while not gmail.is_ready():
            time.sleep(0.1)

        item: tuple[GmailThread, GmailDraft, OllamaClient] = queue_send.get()
        thread, draft, OllamaClient = item

        try:
            thread = gmail.thread_get_automon(thread.id)

            if gmail.is_old(thread):
                if labels.auto_reply in thread._messages_labels:
                    draft_sent = gmail.draft_send(draft=draft)

                    gmail.messages_modify_automon(
                        id=thread.id,
                        addLabelIds=[labels.unread])

                    queue_log.put((f'[processor_draft_send] :: sent :: {draft_sent}', 2))

            queue_send.task_done()

        except Exception as error:
            queue_sent.put((thread, draft, OllamaClient))
            queue_log.put((f'[processor_draft_send] :: ERROR :: {error=}', 1))
            time.sleep(60)


def processor_email_waiting(gmail: AutomonGmailClient):
    while True:

        while not gmail.is_ready():
            time.sleep(0.1)

        thread: GmailThread = queue_waiting.get()

        try:
            thread = gmail.thread_get_automon(thread.id)

            queue_log.put((f'[processor_email_waiting] :: {queue_waiting.qsize()} left :: {thread}', 2))

            if gmail.is_follow_up(thread):
                queue_followup.put(thread)
                queue_waiting.task_done()
                continue

            gmail.messages_modify_automon(
                id=thread.id,
                addLabelIds=[labels.waiting])

            queue_waiting.put(thread)
            queue_waiting.task_done()

            time.sleep(60)

        except Exception as error:
            # queue_waiting.put(thread)
            queue_log.put((f'[processor_email_waiting] :: ERROR :: {error=}', 1))
            time.sleep(60)


def processor_email_followup(gmail: AutomonGmailClient):
    while True:

        while not gmail.is_ready():
            time.sleep(0.1)

        thread: GmailThread = queue_followup.get()

        try:
            gmail.messages_modify_automon(
                id=thread.id,
                removeLabelIds=[labels.waiting])

            queue_log.put((f'[processor_email_followup] :: {queue_followup.qsize()} left :: {thread}', 2))

            identity = RESUME._message_first._email_from
            background = RESUME._message_first._attachments_first.body._data_html_text

            human = HumanAgent(
                name=identity,
                memory=background,
            )

            response, ollama = write_email_followup(identity=human, thread=thread)

            draft = None
            if is_good_reply(response):

                resume_attachment = RESUME_ATTACHMENT

                draft = draft_create(
                    thread=thread,
                    response=response,
                    resume_attachment=resume_attachment,
                )

                if draft is not None:
                    if labels.auto_reply in thread._messages_labels:
                        queue_send.put((thread, draft, ollama))

            queue_followup.task_done()

        except Exception as error:
            # queue_followup.put(thread)
            queue_log.put((f'[processor_email_followup] :: ERROR :: {error=}', 1))
            time.sleep(60)


def processor_token_counter():
    global TOTAL_TOKENS

    while True:
        tokens: int = queue_tokens.get()

        try:
            TOTAL_TOKENS += tokens
            queue_tokens.task_done()

        except Exception as error:
            # queue_tokens.put(tokens)
            queue_log.put((f'[processor_token_counter] :: ERROR :: {error=}', 1))
            time.sleep(60)


def is_job_email(thread: GmailThread) -> bool:
    ollama = OllamaClient(host=random_ollama_host()).set_model(OLLAMA_MODEL)

    ollama.add_prompt(ollama.templates.true_or_false.email_is_job(thread.to_prompt()))

    response = ollama.chat(print_stream=CHAT_STREAM).response()
    return is_true(response)


def is_rejected_email(thread: GmailThread) -> bool:
    ollama = OllamaClient(host=random_ollama_host()).set_model(OLLAMA_MODEL)

    ollama.add_prompt(OllamaClient.templates.true_or_false.email_is_rejected(thread.to_prompt()))

    response = ollama.chat(print_stream=CHAT_STREAM).response()
    return is_true(response)


def write_email_reply(identity: Identity, thread: GmailThread) -> tuple[str, OllamaClient]:
    ollama = OllamaClient(host=random_ollama_host()).set_model(OLLAMA_MODEL)

    ollama.add_system_prompt(AgentTemplates.job_applicant())
    ollama.add_system_prompt(AgentTasks.write_email())
    ollama.add_system_prompt(identity)
    ollama.add_prompt(thread.to_prompt())
    ollama.add_prompt(f'Write a reply to the email.')

    chat = ollama.chat(print_stream=CHAT_STREAM)
    response = chat.response()

    queue_tokens.put(chat._total_tokens)
    return response, ollama


def write_email_followup(identity: Identity, thread: GmailThread) -> tuple[str, OllamaClient]:
    ollama = OllamaClient(host=random_ollama_host()).set_model(OLLAMA_MODEL)

    ollama.add_system_prompt(AgentTasks.write_email())
    ollama.add_system_prompt(identity)
    ollama.add_prompt(thread.to_prompt())
    ollama.add_prompt(f'Reply back to the email sender.')

    chat = ollama.chat(print_stream=CHAT_STREAM)
    response = chat.response()

    queue_tokens.put(chat._total_tokens)
    return response, ollama


def is_good_reply(response) -> bool:
    ollama = OllamaClient(host=random_ollama_host()).set_model(OLLAMA_MODEL)

    ollama.add_prompt(OllamaClient.templates.true_or_false.rules_is_followed(
        rules=OllamaClient.templates.agents.tasks.write_email(),
        text=response
    ))

    chat = ollama.chat(print_stream=CHAT_STREAM)
    response = chat.response()

    queue_tokens.put(chat._total_tokens)
    return is_true(response)


def log_printer():
    while True:
        log, level = queue_log.get()

        if level <= DEBUG_LEVEL:
            debug(log)

        queue_log.task_done()


def run_gemini(prompts: list, chat: bool = False) -> tuple[str, GoogleGeminiClient]:
    gemini = GoogleGeminiClient()
    gemini.set_random_model()
    model = gemini.model
    api = gemini.api_version

    global DF

    if gemini.is_ready():

        # gemini.add_content(role='model', prompt=gemini.prompts.agent_machine_job_applicant)

        prompts = prompts.copy()
        for prompt in prompts:
            gemini.add_content(prompt)

        if chat:
            response = gemini.chat().chat_forever()
        else:
            response = gemini.chat()

        mask = DF['model'] == model
        if mask.any():
            idx = DF[mask].index[0]

            DF.at[idx, 'working_count'] = int(DF.at[idx, 'working_count']) + 1
        else:
            new_event = {
                'model': model,
                'last_error': '',
                'error_count': 0,
                'working_count': 1,
            }
            DF.loc[len(DF)] = new_event
        DF.sort_values(by='working_count', ascending=True, inplace=True, ignore_index=True)

        debug((api, model))
        debug(DF)

        return response, gemini


def run_ollama(prompt: str) -> tuple[str, OllamaClient]:
    ollama = OllamaClient(host=random_ollama_host()).set_model(OLLAMA_MODEL)

    if ollama.is_ready():
        ollama.add_prompt(prompt)
        response = ollama.chat(print_stream=CHAT_STREAM).response()

        return response, ollama


MODEL_ERRORS = {}
import pandas as pd

schema = {
    'model': 'str',
    'last_error': 'str',
    'error_count': 'Int16',
    'working_count': 'Int16',
}

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 2000)
pd.set_option('display.max_colwidth', 120)

MODEL_API_ERROR_DF = pd.DataFrame(columns=schema.keys()).astype(schema)
DF = MODEL_API_ERROR_DF


def run_llm(prompt: str, chat: bool = False) -> tuple[str, object]:
    global MODEL_ERRORS
    global DF

    response = None
    while True:

        if USE_OLLAMA:
            response, model = run_ollama(prompt=prompt)
            break

        try:
            if USE_GEMINI:
                raise debug_exception(locals(), f'fix prompt to use markdown')
                response, model = run_gemini(prompts=prompts, chat=chat)
                break
        except Exception as error:
            if len(error.args) > 1:
                error_ = error.args[1]
                model = error.args[2]

                mask = DF['model'] == model
                if mask.any():
                    idx = DF[mask].index[0]

                    DF.at[idx, 'last_error'] = error_
                    DF.at[idx, 'error_count'] = int(DF.at[idx, 'error_count']) + 1
                else:
                    new_event = {
                        'model': model,
                        'last_error': error_,
                        'error_count': 1,
                        'working_count': 0,
                    }
                    DF.loc[len(DF)] = new_event
                DF.sort_values(by='working_count', ascending=True, inplace=True, ignore_index=True)

                print(DF)

                pass

    return response, model


def draft_create(
        thread: GmailThread,
        response: str,
        resume_attachment: GmailMessagePayload = None,
) -> GmailDraft:
    if resume_attachment is not None:
        assert resume_attachment.filename

    resume_attachment = [gmail.draft_attachment_create(resume_attachment)]

    to = thread._message_first._header_from.value
    from_ = thread._message_first._header_to.value

    # create draft
    body = response
    subject = "Re: " + thread._message_first._header_subject.value
    draft = gmail.draft_create(
        threadId=thread.id,
        draft_to=to,
        draft_cc='dianajaw@gmail.com',
        draft_from=from_,
        draft_subject=subject,
        draft_body=body,
        draft_attachments=resume_attachment,
        include_original=thread._clean_thread_latest
    )
    draft_get = gmail.draft_get_automon(id=draft.id)

    gmail.messages_modify_automon(
        id=thread.id,
        addLabelIds=[labels.unread])

    return draft_get


def main():
    global gemini
    global gmail

    while not gmail.is_ready():
        time.sleep(10)

    gmail.login()
    gmail.config.Credentials()

    threads = ThreadingClient()

    threads.add_worker(target=gmail.create_labels)

    threads.add_worker(target=get_threads, args=(gmail,))
    threads.add_worker(target=get_resume, args=(gmail,))

    threads.add_worker(target=processor_email_thread, args=(gmail,))
    threads.add_worker(target=processor_email_new, args=(gmail,))
    threads.add_worker(target=processor_email_waiting, args=(gmail,))
    threads.add_worker(target=processor_draft_send, args=(gmail,))
    threads.add_worker(target=processor_email_sent, args=(gmail,))
    threads.add_worker(target=processor_email_followup, args=(gmail,))

    threads.add_worker(target=log_printer)
    threads.add_worker(target=processor_token_counter)

    threads.add_worker(target=gmail_token_refresher, args=(gmail,))

    threads.start(max_threads=len(queues))


class MyTestCase(unittest.TestCase):
    def test_something(self):
        while gmail.is_ready():
            main()
        pass


if __name__ == '__main__':
    unittest.main()
