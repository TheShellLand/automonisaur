import unittest

import time
import threading

from queue import Queue

from automon.helpers.threadingWrapper import ThreadingClient
from automon.integrations.google.gmail import *
from automon.integrations.ollamaWrapper import OllamaClient
from automon.integrations.google.gemini import GoogleGeminiClient
from automon import LoggingClient, ERROR, DEBUG, CRITICAL, INFO, debug

DEBUG_LEVEL = 2
DEBUG_ = False
DEFAULT_LEVEL = ERROR

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

USE_OLLAMA = False
USE_GEMINI = True
CHAT_FOREVER = False

gmail = GoogleGmailClient()
gemini = GoogleGeminiClient()

# gmail.config.add_gmail_scopes()
gmail.config.add_scopes([
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
])

labels = gmail._automon_labels

queue_threads: Queue[Thread] = Queue(maxsize=10)
queue_new: Queue[Thread] = Queue(maxsize=10)
queue_send: Queue[tuple[Thread, Draft]] = Queue()
queue_skipped: Queue[Thread] = Queue()
queue_followup: Queue[Thread] = Queue()
queue_analyze: Queue[Thread] = Queue()
queue_waiting_for_first_call: Queue[Thread] = Queue()
queue_waiting_for_interview: Queue[Thread] = Queue()

queue_unknown: Queue[Thread] = Queue()

queue_error: Queue[tuple[Thread, Exception]] = Queue()
queue_log: Queue[str] = Queue()

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


def queue_put(item, queue):
    if item not in queue.queue:
        queue.put(item)


def automon_init(client: GoogleGmailClient):
    pass


def get_threads():
    while gmail.is_ready():

        if queue_threads.full():
            pass

        query_sequence = [
            [labels.automon, labels.error],
            [labels.automon, labels.processing],
            [labels.automon, labels.analyze],
            [labels.automon],
        ]

        nextPageToken = None

        for query in query_sequence:
            thread_search = gmail.thread_list_automon(
                maxResults=1,
                pageToken=nextPageToken,
                labelIds=query,
            )

            for thread in thread_search.threads:

                if thread not in queue_threads.queue:
                    queue_threads.put(thread)
                    # queue_log.put(f'[producer_threads] :: {thread}')
                    queue_log.put(f'[producer_threads] :: {queue_threads.unfinished_tasks} threads :: Thread({thread})')

            nextPageToken = thread_search.nextPageToken


def get_resume():
    global RESUME
    while RESUME is None:
        threads = gmail.thread_list_automon(
            maxResults=1,
            labelIds=[labels.automon, labels.resume]
        )

        for thread in threads.threads:
            if gmail.utils.is_resume(thread):
                queue_threads.put(thread)


def processor_email_thread():
    while True:
        thread = queue_threads.get()

        # queue_log.put(f'[processor_email_thread] :: {thread}')

        # resume
        if GoogleGmailClient.utils.is_resume(thread):
            global RESUME
            RESUME = thread
            queue_threads.task_done()
            continue

        # skipped
        if GoogleGmailClient.utils.is_skipped(thread):
            queue_put(thread, queue_skipped)
            queue_threads.task_done()
            queue_log.put(f'[processor_email_thread] :: queue_skipped :: {queue_skipped.qsize()} threads')
            continue

        # error
        if GoogleGmailClient.utils.is_error(thread):
            queue_put(thread, queue_error)
            queue_threads.task_done()
            queue_log.put(f'[processor_email_thread] :: queue_error :: {queue_error.qsize()} threads')
            continue

        # analyze
        if GoogleGmailClient.utils.is_analyze(thread):
            queue_put(thread, queue_analyze)
            queue_threads.task_done()
            queue_log.put(f'[processor_email_thread] :: queue_analyze :: {queue_analyze.qsize()} threads')
            continue

        # scheduled
        if GoogleGmailClient.utils.is_scheduled(thread):
            pass

        # sent
        if GoogleGmailClient.utils.is_sent(thread):
            if GoogleGmailClient.utils.is_old(thread):
                queue_put(thread, queue_followup)
                queue_threads.task_done()
                queue_log.put(f'[processor_email_thread] :: queue_followup :: {queue_followup.qsize()} threads')
                continue

        # new
        if GoogleGmailClient.utils.is_new(thread):
            queue_put(thread, queue_new)
            queue_threads.task_done()
            queue_log.put(f'[processor_email_thread] :: queue_new :: {queue_new.qsize()} threads')
            continue

        queue_put(thread, queue_unknown)
        queue_log.put(f'[processor_email_thread] :: queue_unknown :: {queue_unknown.qsize()} threads')

        queue_threads.task_done()
        pass


def processor_email_new():
    global RESUME

    PROCESSING = True
    while PROCESSING:
        if RESUME is None:
            import time
            time.sleep(1)
            continue

        thread: Thread = queue_new.get()

        resume_str = RESUME._message_first._attachments_first.parts[0].body._data_html_text()

        prompt = thread.to_prompt()
        prompt.append({'resume': resume_str})

        response_passed = False
        while not response_passed:

            if not is_from_human(prompt):
                gmail.thread_modify(id=thread.id, addLabelIds=[labels.unread, labels.skipped])
                break

            if is_rejected_email(prompt):
                gmail.thread_modify(id=thread.id, addLabelIds=[labels.unread, labels.skipped])
                break

            response, model = get_response(prompt)

            response, model = check_response(prompts=prompt, response=response)

            if gemini.response_is_false(response_passed):
                response_check_loop = False
                while gemini.response_is_false(response_check_loop):
                    response, model = get_response(prompt)
                    response_check_loop, model = check_response(prompts=prompt, response=response)

            else:
                gmail.thread_modify(id=thread.id, addLabelIds=[labels.unread, labels.skipped])

        if response_passed:
            if not GoogleGmailClient.utils.is_skipped(thread_selected):
                if GoogleGmailClient.utils.is_follow_up(thread_selected):
                    draft = draft_create(
                        thread=thread,
                        response=response,
                        thread_selected=thread
                    )

        gmail.messages_modify_automon(
            id=thread._message_first.id,
            removeLabelIds=[labels.processing])

        queue_new.task_done()


def is_from_human(prompts: list) -> bool:
    prompts.append({'question': GoogleGeminiClient.prompts.TrueOrFalseTemplates().email_is_human})
    response, model = run_llm(prompts=prompts, chat=False)
    return gemini.response_is_true(response)


def is_rejected_email(prompts: list) -> bool:
    prompts.append({'question': GoogleGeminiClient.prompts.TrueOrFalseTemplates().email_is_rejected})
    response, model = run_llm(prompts=prompts, chat=False)
    return gemini.response_is_true(response)


def get_response(prompts: list) -> tuple[str, any]:
    prompts.append({'question': GoogleGeminiClient.prompts.AgentTemplates().agent_machine_job_applicant})
    response, model = run_llm(prompts=prompts, chat=chat)
    return response, model


def check_response(prompts: list, response) -> tuple[str, any]:
    prompts_check = prompts
    prompts_check += GoogleGeminiClient.prompts.AgentTemplates().agent_machine_job_applicant
    prompts_check += [f"RESPONSE: {response}"]
    prompts_check += GoogleGeminiClient.prompts.TrueOrFalseTemplates().rules_is_followed

    response_check, model = run_llm(prompts_check)

    if gemini.response_is_false(response_check):
        prompts_fix = prompts + [(
            f"RESPONSE: {response} \n"
            f"first say what portion of the response was wrong, and highlight the wrong part of the response \n"
            f"then write a prompt to fix what was wrong using the format: \n"
            f"RULE: reason goes here"
        )]

        run_llm(prompts=prompts_fix, chat=True)

    return response_check, model


def processor_draft_send(gmail):
    while True:
        item: tuple[Thread, Draft] = queue_send.get()
        thread, draft = item

        draft_sent = gmail.draft_send(draft=draft)

        gmail.messages_modify_automon(
            id=thread._message_first.id,
            addLabelIds=[labels.unread])

        queue_send.task_done()


def processor_email_waiting():
    pass


def log_printer():
    while True:
        log = queue_log.get()
        debug(log)
        queue_log.task_done()


def check_gmail_labels(gmail: GoogleGmailClient):
    if gmail.is_ready():

        labels._reset_labels = True

        def init_automon_labels(label, reset_labels):

            id = label.id
            name = label.name
            color = label.color

            if label.id is None:
                labels_get_by_name = gmail.labels_get_by_name(name)

                if labels_get_by_name is None:
                    label.automon_update(
                        gmail.labels_create(
                            name=name,
                            color=color,
                        )
                    )
                else:
                    if reset_labels:
                        gmail.labels_update(id=labels_get_by_name.id, color=color)

                    label.automon_update(
                        labels_get_by_name
                    )

        _threads = []
        for label in labels.all_labels:
            t = threading.Thread(target=init_automon_labels, args=(label, labels._reset_labels))
            _threads.append(t)
            t.start()

        for t in _threads: t.join()


def run_gemini(prompts: list, chat: bool = False) -> tuple[str, GoogleGeminiClient]:
    gemini = GoogleGeminiClient()
    gemini.set_random_model()

    if gemini.is_ready():

        # gemini.add_content(role='model', prompt=gemini.prompts.agent_machine_job_applicant)

        for prompt in prompts:
            gemini.add_content(prompt)

        if chat:
            gemini_response = gemini.chat().chat_forever().chat_response()
        else:
            gemini_response = gemini.chat().chat_response()

        return gemini_response, gemini


def run_ollama(prompts: list) -> tuple[str, OllamaClient]:
    ollama = OllamaClient()
    ollama.set_model('deepseek-r1:8b')

    if ollama.is_ready():

        # ollama.add_message(role='model', content=ollama.prompts.agent_machine_job_applicant)

        for prompt in prompts:
            ollama.add_message(prompt)

        ollama.set_context_window(ollama.get_total_tokens() * 1.10)
        ollama_response = ollama.chat().chat_response

        import re
        try:
            think_re = re.compile(r"(<think>.*</think>)", flags=re.DOTALL)
            think_ = think_re.search(ollama_response).groups()
            think_ = str(think_).strip()

            response_re = re.compile(r"<think>.*</think>(.*)", flags=re.DOTALL)
            response_ = response_re.search(ollama_response).groups()
            response_ = str(response_[0]).strip()
        except:
            raise

        return response_, ollama


MODEL_ERRORS = {}
import pandas as pd

MODEL_API_ERROR_DF = pd.DataFrame()
DF = MODEL_API_ERROR_DF


def run_llm(prompts: list, chat: bool = False) -> tuple[str, any]:
    global MODEL_ERRORS

    response = None
    while True:
        try:
            if USE_OLLAMA:
                response, model = run_ollama(prompts=prompts)
                break

            if USE_GEMINI:
                response, model = run_gemini(prompts=prompts, chat=chat)
                break
        except Exception as error:
            if len(error.args) > 1:
                error_ = error.args[1].get('error')
                model = error.args[2]

                global DF

                new_error = {
                    'model': model,
                    'error': error_,
                    'error_count': 1
                }

                if DF.empty:
                    DF = pd.DataFrame([new_error])
                else:

                    mask = (DF['model'] == model) & (DF['error'] == error_)

                    if mask.any():
                        DF.loc[mask, 'error_count'] += 1
                    else:
                        DF.loc[len(DF)] = new_error

                DF.sort_values(by='error_count', ascending=True, inplace=True)

                pass

    return response, model


def draft_create(
        thread: Thread,
        response: str,
        thread_selected: Thread,
        resume_attachment: MessagePartBody,
):
    if GoogleGmailClient.utils.is_follow_up(thread):
        resume_attachment = []

    if not GoogleGmailClient.utils.has_doc_attachment(thread):
        resume_attachment = resume_attachment.attachments[1]
        assert resume_attachment.filename

        resume_attachment = gmail.classes.EmailAttachment(
            bytes_=resume_attachment.body._data_base64decoded(),
            filename=resume_attachment.filename,
            mimeType=resume_attachment.mimeType)

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

    check_gmail_labels(gmail)

    threads = ThreadingClient()

    threads.add_worker(target=get_threads)
    threads.add_worker(target=get_resume)

    threads.add_worker(target=processor_email_thread)
    threads.add_worker(target=processor_email_new)
    threads.add_worker(target=processor_draft_send, args=(gmail,))
    threads.add_worker(target=processor_email_waiting)

    threads.add_worker(target=log_printer)

    threads.start(max_threads=len(queues) * 2)


class MyTestCase(unittest.TestCase):
    def test_something(self):
        while gmail.is_ready():
            main()
        pass


if __name__ == '__main__':
    unittest.main()
