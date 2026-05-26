import unittest

import time

from queue import Queue

from automon.helpers import *
from automon.helpers.threadingWrapper import ThreadingClient
from automon.integrations.google.gmail import *
from automon.integrations.ollamaWrapper import OllamaClient
from automon.integrations.google.gemini import GoogleGeminiClient
from automon import LoggingClient, ERROR, DEBUG, CRITICAL, INFO, debug

queue_threads: Queue[Thread] = UniqueQueue(maxsize=5)
queue_new: Queue[Thread] = UniqueQueue(maxsize=5)
queue_send: Queue[tuple[Thread, Draft]] = UniqueQueue()
queue_skipped: Queue[Thread] = UniqueQueue()
queue_followup: Queue[Thread] = UniqueQueue()
queue_waiting: Queue[Thread] = UniqueQueue()
queue_analyze: Queue[Thread] = UniqueQueue()
queue_waiting_for_first_call: Queue[Thread] = UniqueQueue()
queue_waiting_for_interview: Queue[Thread] = UniqueQueue()

queue_unknown: Queue[Thread] = UniqueQueue()
query_history: Queue[Thread] = UniqueQueue()

queue_error: Queue[Thread] = UniqueQueue()
queue_log: Queue[str] = UniqueQueue()

queues = [
    queue_threads,
    queue_new,
    queue_send,
    queue_skipped,
    queue_followup,
    queue_analyze,
    queue_error,
    queue_waiting_for_first_call,
    queue_waiting_for_interview,
    queue_unknown,
    queue_error,
    queue_log,
]

RESUME: Thread = None

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

USE_OLLAMA = True
USE_GEMINI = False
CHAT_FOREVER = False

gmail = AutomonGmailClient()
gemini = GoogleGeminiClient()

# gmail.config.add_gmail_scopes()
gmail.config.add_scopes([
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
])

labels = gmail._labels


def gmail_token_refresher(gmail: AutomonGmailClient):
    while True:
        gmail.config.refresh_token()
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
            queue_log.put(f'[get_threads] :: {query} :: {thread_search}')

            for thread in thread_search.threads:

                if thread not in query_history.queue:
                    query_history.put(thread)
                    queue_threads.put(thread)
                    queue_log.put(f'[get_threads] :: {query_history.qsize()} total')

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

        queue_log.put(f'[processor_email_thread] :: {thread}')

        gmail.clean_drafts(thread)

        # resume
        if gmail.is_resume(thread):
            global RESUME
            RESUME = thread
            queue_threads.task_done()
            continue

        # skipped
        if gmail.is_skipped(thread):
            queue_skipped.put(thread)
            queue_threads.task_done()
            queue_log.put(f'[processor_email_thread] :: queue_skipped :: {queue_skipped.qsize()} threads')
            continue

        # error
        if gmail.is_error(thread):
            queue_error.put(thread)
            queue_threads.task_done()
            queue_log.put(f'[processor_email_thread] :: queue_error :: {queue_error.qsize()} threads')
            continue

        # analyze
        if gmail.is_analyze(thread):
            queue_analyze.put(thread)
            queue_threads.task_done()
            queue_log.put(f'[processor_email_thread] :: queue_analyze :: {queue_analyze.qsize()} threads')
            continue

        # scheduled
        if gmail.is_scheduled(thread):
            pass

        # followup
        if gmail.is_sent(thread):
            if gmail.is_old(thread):
                queue_followup.put(thread)
                queue_threads.task_done()
                queue_log.put(f'[processor_email_thread] :: queue_followup :: {queue_followup.qsize()} threads')
                continue

        # waiting
        if gmail.is_sent(thread):

            gmail.messages_modify_automon(
                id=thread._message_first.id,
                addLabelIds=[labels.waiting])

            thread = gmail.thread_get_automon(id=thread.id)

            if not gmail.is_old(thread):
                queue_waiting.put(thread)
                queue_threads.task_done()
                queue_log.put(f'[processor_email_thread] :: queue_waiting :: {queue_waiting.qsize()} threads')
                continue

        # new
        if gmail.is_new(thread):
            queue_new.put(thread)
            queue_threads.task_done()
            queue_log.put(f'[processor_email_thread] :: queue_new :: {queue_new.qsize()} threads :: {thread}')
            continue

        queue_unknown.put(thread)
        queue_log.put(f'[processor_email_thread] :: queue_unknown :: {queue_unknown.qsize()} threads :: {thread}')

        gmail.messages_modify_automon(
            id=thread._message_first.id,
            removeLabelIds=[labels.processing])

        queue_threads.task_done()
        time.sleep(0.1)

        pass


def processor_email_new(gmail: AutomonGmailClient, gemini: GoogleGeminiClient):
    global RESUME

    _PROCESSING = True
    while _PROCESSING:
        while RESUME is None:
            time.sleep(1)

        thread: Thread = queue_new.get()

        debug(f'[processor_email_new] :: {thread}')

        gmail.messages_modify_automon(
            id=thread._message_first.id,
            addLabelIds=[labels.processing])

        _resume_str = RESUME._message_first._attachments_first.parts[0].body._data_html_text

        prompt = thread.to_prompt()
        prompt.append({'resume': _resume_str})

        response_passed = False
        response = False
        while not response_passed:

            while True:

                try:
                    if not is_from_human(prompt):
                        gmail.thread_modify(id=thread.id, addLabelIds=[labels.unread, labels.skipped])
                        break

                    if is_rejected_email(prompt):
                        gmail.thread_modify(id=thread.id, addLabelIds=[labels.unread, labels.skipped])
                        break

                    response, model = write_email_reply(prompt)
                    if is_good_reply(prompts=prompt, response=response):
                        response_passed = True
                        break

                except Exception as error:
                    pass

        if response_passed:
            if not gmail.is_skipped(thread):
                draft = None

                if gmail.is_new(thread):
                    resume_attachment = RESUME._message_first.find_attachment_docx()

                    draft = draft_create(
                        thread=thread,
                        response=response,
                        thread_selected=thread,
                        resume_attachment=resume_attachment,
                    )

                elif gmail.is_follow_up(thread):

                    draft = draft_create(
                        thread=thread,
                        response=response,
                        thread_selected=thread,
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


def is_from_human(prompts: list) -> bool:
    prompts = prompts.copy()
    prompts.append({'question': GoogleGeminiClient._templates.TrueOrFalseTemplates().email_is_human})
    response, model = run_llm(prompts=prompts, chat=False)
    return gemini.response_is_true(response)


def is_rejected_email(prompts: list) -> bool:
    prompts = prompts.copy()
    prompts.append({'question': GoogleGeminiClient._templates.TrueOrFalseTemplates().email_is_rejected})
    response, model = run_llm(prompts=prompts, chat=False)
    return gemini.response_is_true(response)


def write_email_reply(prompts: list) -> tuple[str, any]:
    prompts = prompts.copy()
    prompts.append({'question': GoogleGeminiClient._templates.AgentTemplates().agent_machine_job_applicant})
    response, model = run_llm(prompts=prompts, chat=False)
    return response, model


def is_good_reply(prompts: list, response) -> bool:
    prompts = prompts.copy()
    prompts.append({'RULES': GoogleGeminiClient._templates.AgentTemplates().agent_machine_job_applicant})
    prompts.append({'RESPONSE': response})
    prompts.append({'question': GoogleGeminiClient._templates.TrueOrFalseTemplates().rules_is_followed})
    response, model = run_llm(prompts)
    return gemini.response_is_true(response)


def processor_draft_send(gmail: AutomonGmailClient):
    while True:
        item: tuple[Thread, Draft] = queue_send.get()
        thread, draft = item

        if labels.auto_reply in thread._messages_labels:
            draft_sent = gmail.draft_send(draft=draft)

            gmail.messages_modify_automon(
                id=thread._message_first.id,
                addLabelIds=[labels.unread])

            debug(f'[processor_draft_send] :: sent :: {draft_sent}')

        queue_send.task_done()
        time.sleep(0.1)


def processor_email_waiting():
    pass


def log_printer():
    while True:
        log = queue_log.get()
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
            response = gemini.chat().chat_forever().response()
        else:
            response = gemini.chat().response()

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


def run_ollama(prompts: list) -> tuple[str, OllamaClient]:
    ollama = OllamaClient()
    ollama.set_model('gemma4:latest')

    if ollama.is_ready():

        # ollama.add_message(role='model', content=ollama.prompts.agent_machine_job_applicant)

        for prompt in prompts:
            ollama.add_prompt(prompt)

        ollama.set_context_window(ollama.get_total_tokens() * 1.10)
        response = ollama.chat().response()

        # import re
        # try:
        #     think_re = re.compile(r"(<think>.*</think>)", flags=re.DOTALL)
        #     think_ = think_re.search(response).groups()
        #     think_ = str(think_).strip()
        #
        #     response_re = re.compile(r"<think>.*</think>(.*)", flags=re.DOTALL)
        #     response_ = response_re.search(response).groups()
        #     response_ = str(response_[0]).strip()
        # except:
        #     raise

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


def run_llm(prompts: list, chat: bool = False) -> tuple[str, object]:
    global MODEL_ERRORS
    global DF

    response = None
    while True:

        if USE_OLLAMA:
            response, model = run_ollama(prompts=prompts)
            break

        try:
            if USE_GEMINI:
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
        thread: Thread,
        response: str,
        thread_selected: Thread,
        resume_attachment: MessagePart = None,
) -> Draft:
    if resume_attachment is not None:
        assert resume_attachment.filename

        resume_attachment = gmail.draft_attachment_create(resume_attachment)

    to = thread._message_first._header_from.value
    from_ = thread._message_first._header_to.value

    # create draft
    body = response
    subject = "Re: " + thread_selected._message_first._header_subject.value
    draft = gmail.draft_create(
        threadId=thread_selected.id,
        draft_to=to,
        draft_from=from_,
        draft_subject=subject,
        draft_body=body,
        draft_attachments=[resume_attachment]
    )
    draft_get = gmail.draft_get_automon(id=draft.id)

    gmail.messages_modify_automon(
        id=thread_selected.id,
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
    threads.add_worker(target=processor_email_new, args=(gmail, gemini))
    threads.add_worker(target=processor_draft_send, args=(gmail,))
    threads.add_worker(target=processor_email_waiting)

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
