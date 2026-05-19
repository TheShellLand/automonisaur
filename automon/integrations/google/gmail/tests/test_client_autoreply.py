import unittest

import time
import threading

from queue import Queue

from automon.helpers.threadingWrapper import ThreadingClient
from automon.integrations.google.gmail import GoogleGmailClient, Thread
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
LoggingClient.logging.getLogger('automon.helpers.threadingWrapper.client').setLevel(DEBUG)

if DEBUG_:
    LoggingClient.logging.getLogger('automon.integrations.google.gemini.client').setLevel(DEBUG)
    LoggingClient.logging.getLogger('automon.integrations.google.gmail.client').setLevel(DEBUG)
else:
    LoggingClient.logging.getLogger('automon.integrations.google.gemini.client').setLevel(CRITICAL)
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
queue_send: Queue[Thread] = Queue()
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

        def search_email(query, pageToken):
            return gmail.thread_list_automon(
                maxResults=1,
                pageToken=pageToken,
                labelIds=query,
            )

        nextPageToken = None

        for query in query_sequence:
            thread_search = search_email(query, nextPageToken)

            for thread in thread_search.threads:
                if thread not in queue_threads.queue:
                    queue_threads.put(thread)
                    # queue_log.put(f'[producer_threads] :: {thread}')
                    queue_log.put(f'[producer_threads] :: {queue_threads.unfinished_tasks} threads')

            nextPageToken = thread_search.nextPageToken


def get_resume():
    while RESUME is None:
        threads = gmail.thread_list_automon(
            maxResults=1,
            labelIds=[labels.automon, labels.resume]
        )

        for thread in threads.threads:
            queue_threads.put(thread)


def processor_email_thread():
    while True:
        thread = queue_threads.get()

        # queue_log.put(f'[processor_email_thread] :: {thread}')

        # resume
        if GoogleGmailClient.utils.is_resume(thread):
            RESUME = thread
            queue_threads.task_done()
            continue

        # skipped
        if GoogleGmailClient.utils.is_skipped(thread):
            queue_skipped.put(thread)
            queue_threads.task_done()
            queue_log.put(f'[processor_email_thread] :: queue_skipped :: {queue_skipped.qsize()} threads')
            continue

        # error
        if GoogleGmailClient.utils.is_error(thread):
            queue_error.put(thread)
            queue_threads.task_done()
            queue_log.put(f'[processor_email_thread] :: queue_error :: {queue_error.qsize()} threads')
            continue

        # analyze
        if GoogleGmailClient.utils.is_analyze(thread):
            queue_analyze.put(thread)
            queue_threads.task_done()
            queue_log.put(f'[processor_email_thread] :: queue_analyze :: {queue_analyze.qsize()} threads')
            continue

        # scheduled
        if GoogleGmailClient.utils.is_scheduled(thread):
            pass

        # sent
        if GoogleGmailClient.utils.is_sent(thread):
            if GoogleGmailClient.utils.is_old(thread):
                queue_followup.put(thread)
                queue_threads.task_done()
                queue_log.put(f'[processor_email_thread] :: queue_followup :: {queue_followup.qsize()} threads')
                continue

        # new
        if GoogleGmailClient.utils.is_new(thread):
            queue_new.put(thread)
            queue_threads.task_done()
            queue_log.put(f'[processor_email_thread] :: queue_new :: {queue_new.qsize()} threads')
            continue

        queue_unknown.put(thread)
        queue_log.put(f'[processor_email_thread] :: queue_unknown :: {queue_unknown.qsize()} threads')

        queue_threads.task_done()
        pass


def processor_email_new():
    while True:
        thread = queue_new.get()

        queue_new.task_done()


def processor_email_send():
    pass


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

MODEL_API_ERROR_QUEUE = Queue()


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
                model = error.args[1]
                MODEL_ERRORS[model] = MODEL_ERRORS.get(model, 0) + 1

                flipped = []
                for model, count in MODEL_ERRORS.items():
                    flipped.append((count, model))

                # 2. Sort it (Python sorts by the first item, which is the count)
                flipped.sort()

                # 3. Flip it back into a dict: {'ollama': 2, 'gemini': 5}
                MODEL_ERRORS = {}
                for count, model in flipped:
                    MODEL_ERRORS[model] = count

                MODEL_API_ERROR_QUEUE.put(response)
                debug(f"[run_llm] :: ERROR :: {MODEL_API_ERROR_QUEUE.qsize()} errors :: {MODEL_ERRORS}")

    if not response:
        raise Exception(f"[run_llm] :: ERROR :: missing llm response :: {response=}")

    return response, model


def draft_create(
        thread,
        response,
        thread_selected,
):
    if GoogleGmailClient.utils.is_follow_up(thread):
        resume_attachment = []

    if not GoogleGmailClient.utils.has_doc_attachment(thread):
        resume_attachment = resume_selected.attachments[1]
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

    gmail.messages_modify(
        id=thread_selected.id,
        addLabelIds=[labels.unread])

    return draft_get


def draft_send(
        draft,
        thread_selected
):
    draft_sent = gmail.draft_send(draft=draft)
    gmail.messages_modify(
        id=thread_selected._message_first.id,
        addLabelIds=[labels.unread])
    return draft_sent


def main():
    global gemini

    # init
    # _welcome_email = gmail.messages_list_automon(labelIds=[labels.automon, labels.welcome])
    # if _welcome_email.automon_messages:
    #     gmail.messages_trash(id=_welcome_email.automon_messages[0].id)

    check_gmail_labels(gmail)

    thread = None
    thread_selected = None

    _FOLLOW_UP = None

    threads = ThreadingClient()

    threads.add_worker(target=get_threads)
    threads.add_worker(target=get_resume)

    threads.add_worker(target=processor_email_thread)
    threads.add_worker(target=processor_email_new)
    threads.add_worker(target=processor_email_send)
    threads.add_worker(target=processor_email_waiting)

    threads.add_worker(target=log_printer)

    threads.start(max_threads=len(queues) * 2)

    resume_selected = resume_search.messages[0]

    resume = resume_selected._attachments_first
    resume = resume.parts[0].body._data_html_text()

    prompts_resume = [f"This is your resume: <RESUME>{resume}</RESUME>\n\n", ]

    i = 1
    prompts_emails = []
    prompts_emails_all = []
    for message in thread_selected.automon_messages:

        if labels.draft in message.labelIds:
            continue

        _message = f"{message.to_prompt()}"

        if labels.draft not in message.labelIds:
            prompts_emails.append(
                f"This is email {i} in an email chain: {_message}\n\n"
            )

        prompts_emails_all.append(
            f"This is email {i} in an email chain: {_message}\n\n"
        )

        i += 1

    if not prompts_emails:
        return

    response = None
    for message in thread_selected.automon_messages:
        if labels.analyze in message.labelIds:
            if labels.sent in thread_selected.automon_message_latest.labelIds:
                break

            _draft = thread_selected.automon_message_latest
            _resume = _draft._attachments_first.body._data_html_text()

            prompts = [_resume] + [f"Give me an analysis of the resume. \n"]
            response, model = run_llm(prompts=prompts, chat=False)

            gmail.messages_modify(id=_draft.id, removeLabelIds=[labels.analyze])
            gmail.messages_trash(id=_draft.id)
            break

    response_check = False
    while not response_check:

        def is_from_human(prompts: list) -> bool:
            prompts_check = prompts + GoogleGeminiClient.prompts.TrueOrFalseTemplates().email_is_human
            response, model = run_llm(prompts=prompts_check, chat=False)
            return gemini.response_is_true(response)

        def is_rejected_email(prompts: list) -> bool:
            prompts_check = prompts
            prompts_check += GoogleGeminiClient.prompts.TrueOrFalseTemplates().email_is_rejected

            response, model = run_llm(prompts=prompts_check, chat=False)
            return gemini.response_is_true(response)

        def get_response(prompts: list) -> tuple[str, any]:
            prompts_ask = prompts + [GoogleGeminiClient.prompts.AgentTemplates().agent_machine_job_applicant]

            chat = False

            if labels.error in thread_selected.automon_messages_labels:
                chat = True

            response, model = run_llm(prompts=prompts_ask, chat=chat)

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

        prompts = prompts_resume + prompts_emails

        if is_from_human(prompts):
            if not is_rejected_email(prompts):
                response, model = get_response(prompts)
                response_check, model = check_response(prompts=prompts, response=response)

                if gemini.response_is_false(response_check):
                    response_check_loop = False
                    while gemini.response_is_false(response_check_loop):
                        response, model = get_response(prompts)
                        response_check_loop, model = check_response(prompts=prompts, response=response)

        else:
            gmail.thread_modify(id=thread.id, addLabelIds=[labels.unread, labels.skipped])

    gmail.config.refresh_token()

    if not GoogleGmailClient.utils.is_skipped(thread_selected):
        if GoogleGmailClient.utils.is_follow_up(thread_selected):
            draft = draft_create(
                thread=thread,
                response=response,
                thread_selected=thread_selected
            )
            draft_send(
                draft=draft,
                thread_selected=thread_selected
            )

            gmail.messages_modify(
                id=thread_selected.automon_message_first.id,
                addLabelIds=[labels.unread])

    gmail.messages_modify(
        id=thread_selected.automon_message_first.id,
        removeLabelIds=[labels.processing])


class MyTestCase(unittest.TestCase):
    def test_something(self):
        while gmail.is_ready():
            main()
        pass


if __name__ == '__main__':
    unittest.main()
