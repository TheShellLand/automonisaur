import unittest

import datetime
import dateutil.parser

from automon.integrations.google.gmail import GoogleGmailClient
from automon import LoggingClient, ERROR, DEBUG, CRITICAL, INFO
from automon.integrations.ollamaWrapper import OllamaClient
from automon.integrations.google.gemini import GoogleGeminiClient

DEBUG_LEVEL = 2
DEBUG_ = False
INFO_ = True

LoggingClient.logging.getLogger('httpx').setLevel(ERROR)
LoggingClient.logging.getLogger('httpcore').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.client').setLevel(DEBUG)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.utils').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.chat').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.requestsWrapper.client').setLevel(CRITICAL)
LoggingClient.logging.getLogger('automon.integrations.google.oauth.config').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.google.gemini.config').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.google.gemini.client').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.google.gmail.client').setLevel(ERROR)
LoggingClient.logging.getLogger('opentelemetry.instrumentation.instrumentor').setLevel(ERROR)

if INFO_:
    LoggingClient.logging.getLogger('automon.integrations.google.gemini.client').setLevel(INFO)
    LoggingClient.logging.getLogger('automon.integrations.google.gmail.client').setLevel(INFO)

if DEBUG_:
    LoggingClient.logging.getLogger('automon.integrations.google.gemini.client').setLevel(DEBUG)
    LoggingClient.logging.getLogger('automon.integrations.google.gmail.client').setLevel(DEBUG)


def debug(log: str, level: int = 1, **kwargs):
    global DEBUG_LEVEL

    if level <= DEBUG_LEVEL:
        print(f"{log}", **kwargs)


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

import threading

if gmail.is_ready():

    labels = gmail._automon_labels
    labels._reset_labels = True


    def init_automon_labels(label, reset_labels):

        id = label.id
        name = label.name
        color = label.color

        if label.id is None:
            labels_get_by_name = gmail.labels_get_by_name(name)

            if labels_get_by_name is None:
                label._update(
                    gmail.labels_create(
                        name=name,
                        color=color,
                    )
                )
            else:
                if reset_labels:
                    gmail.labels_update(id=labels_get_by_name.id, color=color)

                label._update(
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


def run_llm(prompts: list, chat: bool = False) -> tuple[str, any]:
    debug([f"{len(x.split(' ')):,}" for x in prompts])

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
            debug(f"[run_llm] :: ERROR :: {error=}")

    if not response:
        raise Exception(f"[run_llm] :: ERROR :: missing llm response")

    return response, model


def main():
    global gemini

    # init
    # _welcome_email = gmail.messages_list_automon(labelIds=[labels.automon, labels.welcome])
    # if _welcome_email.automon_messages:
    #     gmail.messages_trash(id=_welcome_email.automon_messages[0].id)

    thread = None
    _nextPageToken = None

    _FOUND = None
    _FOLLOW_UP = None
    while gmail.is_ready():

        _FOUND = None
        _FOLLOW_UP = None

        # search labels.retry first
        email_search = gmail.thread_list_automon(
            maxResults=1,
            pageToken=_nextPageToken,
            labelIds=[labels.automon, labels.retry],
        )

        if not email_search:
            email_search = gmail.thread_list_automon(
                maxResults=1,
                pageToken=_nextPageToken,
                labelIds=[labels.automon],
            )

        _nextPageToken = email_search.nextPageToken

        if not email_search.threads:
            debug('_', end='')
            continue

        for thread in email_search.automon_threads:

            # thread = gmail.thread_get_automon('195da1cbcaa5573b')

            _first = thread.automon_message_first
            _latest = thread.automon_message_latest

            debug(f"{_latest.automon_date_since_now_str} :: "
                  f"{thread.automon_messages_count} messages ::"
                  f"{thread.id} :: "
                  f"{_first.automon_payload.get_header('subject')} :: "
                  f"{_first.automon_labels} :: ", end='', level=2)

            # resume
            if labels.resume in _first.automon_labels:
                continue

            # analyze
            if (labels.analyze in _first.automon_labels
            ):
                _FOUND = True
                debug('analyze', end='')
                break

            # draft
            if (labels.draft in _latest.automon_labels
                    and labels.trash not in _latest.automon_labels
            ):
                continue

            # auto
            if ((labels.auto_reply_enabled in _first.automon_labels
                 or labels.auto_reply_enabled in _latest.automon_labels)
                    and (labels.sent not in _latest.automon_labels)
            ):
                _FOUND = True
                debug('auto', end='')
                break

            # sent
            if labels.sent in _latest.automon_labels:

                if _latest.automon_date_since_now.days >= 3:
                    _FOUND = True
                    _FOLLOW_UP = True
                    debug('followup', end='')
                    break

                continue

            # new
            if labels.sent not in _latest.automon_labels:
                _sent = False

                if labels.draft not in _latest.automon_labels:
                    _FOUND = True
                    debug('new', end='')
                    break

                continue

        if _FOUND:
            break

        debug("\n")

    resume_search = gmail.messages_list_automon(
        maxResults=1,
        labelIds=[labels.resume]
    )

    # retry
    for _message in thread.automon_messages:

        # delete DRAFT
        if labels.draft in _message.automon_labels:
            gmail.messages_trash(id=_message.id)

    email_selected = thread
    resume_selected = resume_search.automon_messages[0]

    resume = resume_selected.automon_attachments_first.automon_parts[0].automon_body.automon_data_html_text()

    to = email_selected.automon_message_first.automon_header_from.value
    from_ = email_selected.automon_message_first.automon_header_to.value

    prompts_base = []
    prompts_resume = [f"This is your resume: <RESUME>{resume}</RESUME>\n\n", ]

    i = 1
    prompts_emails = []
    prompts_emails_all = []
    for message in email_selected.automon_messages:

        if labels.draft in message.automon_labels:
            continue

        _message = f"{message.to_dict()}"

        import re

        _del = re.compile(r"'data': ('[a-zA-Z0-9-_=]+')").findall(_message)
        for _x in _del:
            _message = _message.replace(_x, "''")

        if labels.draft not in message.automon_labels:
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
    for _message in email_selected.automon_messages:
        if labels.analyze in _message.automon_labels:
            if labels.sent in email_selected.automon_message_latest.automon_labels:
                break

            _draft = email_selected.automon_message_latest
            _resume = _draft.automon_attachments.attachments[0].automon_body.automon_data_html_text

            prompts = [_resume] + [f"Give me an analysis of the resume. \n"]
            response, model = run_llm(prompts=prompts, chat=False)

            gmail.messages_modify(id=_draft.id, removeLabelIds=[labels.analyze])
            gmail.messages_trash(id=_draft.id)
            break

    while True:

        if response is None:
            prompts = prompts_resume + prompts_emails
            prompts.append(
                GoogleGeminiClient.prompts.agent_machine_job_applicant,
            )

            if [x for x in email_selected.automon_messages if labels.retry in x.automon_labels]:
                response, model = run_llm(prompts=prompts, chat=True)
            else:
                response, model = run_llm(prompts=prompts, chat=False)

            double_check_prompts = prompts_resume + prompts_emails
            double_check_prompts.append(
                f"RULES: {GoogleGeminiClient.prompts.agent_machine_job_applicant}"
            )
            double_check_prompts.append(
                f"RESPONSE: {response}"
            )
            double_check_prompts.append(
                f"Respond True or False. Is the RESPONSE following all RULES?"
            )
            check, model = run_llm(double_check_prompts)

            if gemini.true_or_false(check):
                break
            else:
                double_check_prompts.append(
                    f"say which rule was violated"
                )
                double_check_prompts.append(
                    f"write a prompt to fix what was wrong"
                )

                test = run_llm(prompts=double_check_prompts, chat=True)

                check, model = run_llm(prompts=double_check_prompts, chat=False)
                prompts.append(check)

    gmail.config.refresh_token()

    if _FOLLOW_UP:
        resume_attachment = []
    else:
        resume_attachment = resume_selected.automon_attachments[1]
        assert resume_attachment.filename

        resume_attachment = gmail.v1.EmailAttachment(
            bytes_=resume_attachment.automon_body.automon_data_base64decoded(),
            filename=resume_attachment.filename,
            mimeType=resume_attachment.mimeType)

    # create draft
    body = response
    subject = "Re: " + email_selected.automon_message_first.automon_header_subject.value
    draft = gmail.draft_create(
        threadId=email_selected.id,
        draft_to=to,
        draft_from=from_,
        draft_subject=subject,
        draft_body=body,
        draft_attachments=[resume_attachment]
    )
    draft_get = gmail.draft_get_automon(id=draft.id)

    gmail.messages_modify(id=email_selected.id,
                          addLabelIds=[labels.unread],
                          removeLabelIds=[labels.retry]
                          )

    if (labels.auto_reply_enabled in email_selected.automon_message_latest.automon_labels
            and labels.sent not in email_selected.automon_message_latest.automon_labels
    ):
        draft_sent = gmail.draft_send(draft=draft)
        gmail.messages_modify(id=email_selected.automon_message_first.id,
                              addLabelIds=[labels.unread])

    # prompts = [prompts_emails[0]] + prompts_resume
    # prompts.append(
    #     f"Respond only true or false, is the job relevant?"
    # )
    # response, model = run_llm(prompts)
    # if gemini.true_or_false(response):
    #     gmail.messages_modify(id=email_selected.id, addLabelIds=[labels.relevant])
    #
    # prompts = [prompts_emails[0]]
    # prompts.append(
    #     f"Respond only true or false, is the job fully and completely remote, with no in-office days?"
    # )
    # response, model = run_llm(prompts)
    # if gemini.true_or_false(response):
    #     gmail.messages_modify(id=email_selected.id, addLabelIds=[labels.remote])

    CHAT_ONCE = 0


class MyTestCase(unittest.TestCase):
    def test_something(self):
        while gmail.is_ready():
            main()
        pass


if __name__ == '__main__':
    unittest.main()
