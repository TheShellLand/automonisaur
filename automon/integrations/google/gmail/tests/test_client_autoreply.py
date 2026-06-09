import unittest

import time

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

queue_threads: Queue[GmailThread] = UniqueQueue(maxsize=5)
queue_new: Queue[GmailThread] = UniqueQueue(maxsize=5)
queue_send: Queue[tuple[GmailThread, GmailDraft]] = UniqueQueue()
queue_skipped: Queue[GmailThread] = UniqueQueue()
queue_followup: Queue[GmailThread] = UniqueQueue()
queue_sent: Queue[GmailThread] = UniqueQueue()
queue_waiting: Queue[GmailThread] = UniqueQueue()
queue_analyze: Queue[GmailThread] = UniqueQueue()
queue_waiting_for_first_call: Queue[GmailThread] = UniqueQueue()
queue_waiting_for_interview: Queue[GmailThread] = UniqueQueue()

queue_unknown: Queue[GmailThread] = UniqueQueue()
query_history: Queue[GmailThread] = UniqueQueue()

queue_error: Queue[GmailThread] = UniqueQueue()
queue_log: Queue[tuple[str, int]] = UniqueQueue()

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
]

"""

logging settings

"""

DEBUG_LEVEL = 2
DEBUG_ = False
DEFAULT_LEVEL = CRITICAL

LoggingClient.logging.getLogger('httpx').setLevel(DEFAULT_LEVEL)
LoggingClient.logging.getLogger('httpcore').setLevel(DEFAULT_LEVEL)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.client').setLevel(DEFAULT_LEVEL)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.utils').setLevel(DEFAULT_LEVEL)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.chat').setLevel(DEFAULT_LEVEL)
LoggingClient.logging.getLogger('automon.integrations.requestsWrapper.client').setLevel(CRITICAL)
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
    LoggingClient.logging.getLogger('automon.integrations.google.gmail.client').setLevel(CRITICAL)

"""

llm settings

"""

USE_OLLAMA = True
USE_GEMINI = False
CHAT_FOREVER = False
CHAT_STREAM = True
USE_GPU = True

if USE_GPU:
    OLLAMA_HOST = 'http://192.168.111.175:11434'
else:
    OLLAMA_HOST = None
OLLAMA_MODEL = 'gemma4:12b'

gemini = GoogleGeminiClient()

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


def gmail_token_refresher(gmail: AutomonGmailClient):
    while True:
        if gmail.config.refresh_token():
            time.sleep(60)

        time.sleep(60)


def automon_init(client: AutomonGmailClient):
    pass


def get_threads(gmail: AutomonGmailClient):
    while True:
        while not gmail.is_ready():
            time.sleep(0.1)

        query_sequence = [
            [labels.automon, labels.error],
            [labels.automon, labels.processing],
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

                if thread not in query_history.queue:
                    query_history.put(thread)
                    queue_threads.put(thread)
                    queue_log.put((f'[get_threads] :: {query_history.qsize()} processed', 3))

            nextPageToken = thread_search.nextPageToken

        time.sleep(0.1)


def get_resume(gmail: AutomonGmailClient):
    global RESUME
    while RESUME is None:
        threads = gmail.thread_list_automon(
            maxResults=1,
            labelIds=[labels.automon, labels.resume]
        )

        for thread in threads.threads:
            if gmail.is_resume(thread):
                RESUME = thread


def processor_email_thread(gmail: AutomonGmailClient):
    while True:
        thread = queue_threads.get()

        queue_log.put((f'[processor_email_thread] :: {thread}', 3))

        # resume
        if gmail.is_resume(thread):
            global RESUME
            RESUME = thread
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

        # sent
        if gmail.is_sent(thread):

            thread = gmail.thread_get_automon(id=thread.id)

            if gmail.is_old(thread):
                queue_followup.put(thread)
                queue_threads.task_done()
                continue
            else:
                queue_waiting.put(thread)
                queue_threads.task_done()
                continue

        # followup
        if gmail.is_follow_up(thread):
            queue_followup.put(thread)
            queue_threads.task_done()
            continue

        queue_unknown.put(thread)
        queue_log.put((f'[processor_email_thread] :: queue_unknown :: {queue_unknown.qsize()} threads :: {thread}', 2))

        gmail.messages_modify_automon(
            id=thread._message_first.id,
            removeLabelIds=[labels.processing])

        queue_threads.task_done()
        time.sleep(0.1)

        pass


def processor_email_new(gmail: AutomonGmailClient):
    global RESUME

    _PROCESSING = True
    while _PROCESSING:
        while RESUME is None:
            time.sleep(1)

        thread: GmailThread = queue_new.get()

        queue_log.put((f'[processor_email_new] :: {thread}', 2))

        gmail.messages_modify_automon(
            id=thread._message_first.id,
            addLabelIds=[labels.processing])

        resume_str = RESUME._message_first._attachments_first.parts[0].body._data_html_text
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
                if not is_from_human(thread):
                    gmail.thread_modify(id=thread.id, addLabelIds=[labels.unread, labels.skipped])
                    exit_loop = True
                    break

                if is_rejected_email(thread):
                    gmail.thread_modify(id=thread.id, addLabelIds=[labels.unread, labels.skipped])
                    exit_loop = True
                    break

                response, model = write_email_reply(identity=human, thread=thread)
                if is_good_reply(response=response):
                    response_passed = True
                    exit_loop = True
                    break


            except Exception as error:
                ollama = OllamaClient(host=OLLAMA_HOST).set_model(OLLAMA_MODEL)
                ollama.add_system_prompt(content=human)
                ollama.add_prompt(thread.to_prompt())
                ollama.chat_forever()
                raise debug_exception(locals(), error)

        if response_passed:
            if not gmail.is_skipped(thread):
                draft = None

                if gmail.is_new(thread):
                    resume_attachment = RESUME._message_first.find_attachment_docx()

                    draft = draft_create(
                        thread=thread,
                        response=response,
                        resume_attachment=resume_attachment,
                    )

                if draft is not None:
                    if labels.auto_reply in thread._messages_labels:
                        queue_send.put((thread, draft))

        gmail.messages_modify_automon(
            id=thread._message_first.id,
            removeLabelIds=[labels.processing],
            addLabelIds=[labels.waiting])

        queue_new.task_done()
        time.sleep(0.1)


def processor_email_sent(gmail: AutomonGmailClient):
    while True:
        thread = queue_sent.get()
        queue_log.put((f'[processor_email_sent] :: {queue_sent.qsize()} left :: {thread}', 2))

        if gmail.is_old(thread):
            queue_followup.put(thread)
            queue_sent.task_done()
            continue

        gmail.messages_modify_automon(
            id=thread._message_first.id,
            addLabelIds=[labels.waiting])

        queue_sent.task_done()


def processor_draft_send(gmail: AutomonGmailClient):
    while True:
        item: tuple[GmailThread, GmailDraft] = queue_send.get()
        thread, draft = item

        if labels.auto_reply in thread._messages_labels:
            draft_sent = gmail.draft_send(draft=draft)

            gmail.messages_modify_automon(
                id=thread._message_first.id,
                addLabelIds=[labels.unread])

            queue_log.put((f'[processor_draft_send] :: sent :: {draft_sent}', 2))

        queue_send.task_done()
        time.sleep(0.1)


def processor_email_waiting(gmail: AutomonGmailClient):
    while True:
        thread: GmailThread = queue_waiting.get()

        queue_log.put((f'[processor_email_waiting] :: {queue_waiting.qsize()} left :: {thread}', 2))

        if gmail.is_old(thread):
            queue_followup.put(thread)
            queue_waiting.task_done()
            continue

        queue_waiting.task_done()


def processor_email_followup(gmail: AutomonGmailClient):
    while True:
        thread: GmailThread = queue_followup.get()
        queue_log.put((f'[processor_email_followup] :: {queue_followup.qsize()} left :: {thread}', 2))

        identity = RESUME._message_first._email_from
        background = RESUME._message_first._attachments_first.parts[0].body._data_html_text

        human = HumanAgent(
            name=identity,
            memory=background,
        )

        response, ollama = write_email_followup(identity=human, thread=thread)

        draft = None
        if is_good_reply(response):

            draft = draft_create(
                thread=thread,
                response=response,
            )

            if draft is not None:
                if labels.auto_reply in thread._messages_labels:
                    queue_send.put((thread, draft))

        gmail.messages_modify_automon(
            id=thread.id,
            addLabelIds=[labels.waiting, labels.unread],
        )

        queue_followup.task_done()


def is_from_human(thread: GmailThread) -> bool:
    ollama = OllamaClient(host=OLLAMA_HOST).set_model(OLLAMA_MODEL)

    ollama.add_prompt(
        ollama.templates.true_or_false.email_is_human(thread.to_prompt())
    )

    response = ollama.chat(print_stream=True).response()
    return is_true(response)


def is_rejected_email(thread: GmailThread) -> bool:
    ollama = OllamaClient(host=OLLAMA_HOST).set_model(OLLAMA_MODEL)

    ollama.add_prompt(
        content=OllamaClient.templates.true_or_false.email_is_rejected(email=thread.to_prompt()),
    )

    response = ollama.chat(print_stream=True).response()
    return is_true(response)


def write_email_reply(identity: Identity, thread: GmailThread) -> tuple[str, object]:
    ollama = OllamaClient(host=OLLAMA_HOST).set_model(OLLAMA_MODEL)

    ollama.add_system_prompt(content=ollama.templates.agents.job_applicant())
    ollama.add_system_prompt(content=OllamaClient.templates.agents.tasks.email_response())
    ollama.add_system_prompt(content=identity.content)
    ollama.add_prompt(content=thread.to_prompt())

    chat = ollama.chat(print_stream=CHAT_STREAM)
    response = chat.response()
    return response, ollama


def write_email_followup(identity: Identity, thread: GmailThread) -> tuple[str, object]:
    ollama = OllamaClient(host=OLLAMA_HOST).set_model(OLLAMA_MODEL)

    ollama.add_system_prompt(content=AgentTasks.email_response())
    ollama.add_system_prompt(content=identity.content)
    ollama.add_prompt(
        content=Markdown.str_to_markdown(
            header='email followup instructions',
            text='Reply back to email sender.'
        ))
    ollama.add_prompt(content=thread.to_prompt())

    chat = ollama.chat(print_stream=CHAT_STREAM)
    response = chat.response()
    return response, ollama


def is_good_reply(response) -> bool:
    ollama = OllamaClient(host=OLLAMA_HOST).set_model(OLLAMA_MODEL)

    _rules = OllamaClient.templates.agents.job_applicant()
    _response = OllamaClient.templates.markdown.str_to_markdown(header='response', text=response)

    ollama.add_system_prompt(
        content=Markdown.str_to_markdown(
            header='question',
            text=OllamaClient.templates.true_or_false.rules_is_followed(rules=_rules, text=_response)
        )
    )

    response = ollama.chat(print_stream=CHAT_STREAM).response()
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
    ollama = OllamaClient(host=OLLAMA_HOST).set_model(OLLAMA_MODEL)

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
        resume_attachment: GmailMessagePart = None,
) -> GmailDraft:
    if resume_attachment is not None:
        assert resume_attachment.filename

        resume_attachment = [gmail.draft_attachment_create(resume_attachment)]
    else:
        resume_attachment = []

    to = thread._message_first._header_from.value
    from_ = thread._message_first._header_to.value

    # create draft
    body = response
    subject = "Re: " + thread._message_first._header_subject.value
    draft = gmail.draft_create(
        threadId=thread.id,
        draft_to=to,
        draft_from=from_,
        draft_subject=subject,
        draft_body=body,
        draft_attachments=resume_attachment
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
        time.sleep(1)

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

    threads.add_worker(target=gmail_token_refresher, args=(gmail,))

    threads.start()


class MyTestCase(unittest.TestCase):
    def test_something(self):
        while gmail.is_ready():
            main()
        pass


if __name__ == '__main__':
    unittest.main()
