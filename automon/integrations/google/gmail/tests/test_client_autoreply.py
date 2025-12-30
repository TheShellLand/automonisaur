import unittest

import threading
from idlelib.rpc import response_queue

from automon.integrations.google.gmail import GoogleGmailClient
from automon import LoggingClient, ERROR, DEBUG, CRITICAL, INFO
from automon.integrations.ollamaWrapper import OllamaClient
from automon.integrations.google.gemini import GoogleGeminiClient

DEBUG_LEVEL = 2
DEBUG_ = True
INFO_ = False

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

labels = gmail._automon_labels


def gmail_labels(gmail: GoogleGmailClient):
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


def run_llm(prompts: list, chat: bool = False) -> tuple[str, any]:
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

    gmail_labels(gmail)

    thread = None
    _nextPageToken = None

    _FOUND = None
    _FOLLOW_UP = None

    while gmail.is_ready():

        _FOUND = None
        _FOLLOW_UP = None

        search_sequence = [
            [labels.automon, labels.processing],
            [labels.automon, labels.chat],
            [labels.automon, labels.analyze],
            [labels.automon],
        ]

        email_search = None
        while True:

            email_search = None

            for _sequence in search_sequence:

                email_search = gmail.thread_list_automon(
                    maxResults=1,
                    pageToken=_nextPageToken,
                    labelIds=_sequence,
                )

                if email_search:
                    break

            if email_search:
                break

        _nextPageToken = email_search.nextPageToken

        if not email_search.threads:
            debug('_', end='')
            continue

        for thread in email_search.automon_threads:

            # thread = gmail.thread_get_automon(thread.id)

            _first = thread.automon_message_first
            _latest = thread.automon_message_latest
            _latest_clean = thread.automon_clean_thread_latest

            debug(f"{_latest_clean.automon_date_since_now_str} :: "
                  f"{thread.automon_messages_count} messages :: "
                  f"{thread.id} :: "
                  f"{_first.automon_payload.get_header('subject')} :: ",
                  end='', level=2)

            gmail.messages_modify(id=_first.id, addLabelIds=[labels.processing])

            # resume
            if labels.resume in thread.automon_messages_labels:
                gmail.messages_modify(id=_first.id, removeLabelIds=[labels.processing])
                continue

            # error
            if labels.error in thread.automon_messages_labels:
                gmail.messages_modify(id=_first.id, removeLabelIds=[labels.processing])
                continue

            # chat
            if labels.chat in thread.automon_messages_labels:
                _FOUND = True
                CHAT = True
                debug('chat')
                break

            # analyze
            if labels.analyze in thread.automon_messages_labels:
                _FOUND = True
                debug('analyze')
                break

            # scheduled
            if labels.scheduled in thread.automon_messages_labels:
                debug('scheduled')
                continue

            # sent
            if labels.sent in _latest_clean.automon_labels:

                if _latest_clean.automon_date_since_now.days >= 3:
                    _FOUND = True
                    _FOLLOW_UP = True
                    debug('followup')
                    break

                gmail.messages_modify(id=_first.id, removeLabelIds=[labels.processing])
                continue

            # new
            if labels.sent not in _latest_clean.automon_labels:
                _FOUND = True
                debug('new')
                break

            gmail.messages_modify(id=_first.id, removeLabelIds=[labels.processing])

        if _FOUND:
            break

    resume_search = gmail.messages_list_automon(
        maxResults=1,
        labelIds=[labels.automon, labels.resume]
    )

    for message in thread.automon_messages:

        # delete DRAFT
        if labels.draft in message.automon_labels:
            gmail.messages_trash(id=message.id)

    email_selected = thread
    resume_selected = resume_search.automon_messages[0]

    resume = resume_selected.automon_attachments().__next__()
    resume = resume.automon_parts[0].automon_body.automon_data_html_text

    prompts_base = []
    prompts_resume = [f"This is your resume: <RESUME>{resume}</RESUME>\n\n", ]

    i = 1
    prompts_emails = []
    prompts_emails_all = []
    for message in email_selected.automon_messages:

        if labels.draft in message.automon_labels:
            continue

        _message = f"{message.to_prompt()}"

        import re

        # _del = re.compile(r"'data': ('[a-zA-Z0-9-_=]+')").findall(_message)
        # for _x in _del:
        #     _message = _message.replace(_x, "''")

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
    for message in email_selected.automon_messages:
        if labels.analyze in message.automon_labels:
            if labels.sent in email_selected.automon_message_latest.automon_labels:
                break

            _draft = email_selected.automon_message_latest
            _resume = _draft.automon_attachments.attachments[0].automon_body.automon_data_html_text

            prompts = [_resume] + [f"Give me an analysis of the resume. \n"]
            response, model = run_llm(prompts=prompts, chat=False)

            gmail.messages_modify(id=_draft.id, removeLabelIds=[labels.analyze])
            gmail.messages_trash(id=_draft.id)
            break

    FAILED = None
    while True:

        def get_response(*args, **kwargs):
            prompts = prompts_resume + prompts_emails
            prompts.append(
                GoogleGeminiClient.prompts.agent_machine_job_applicant,
            )

            if (labels.chat in email_selected.automon_messages_labels):
                response, model = run_llm(prompts=prompts, chat=True)
            else:
                response, model = run_llm(prompts=prompts, chat=False)

            return response, model

        def check_response(response):
            double_check_prompts = prompts_resume + prompts_emails
            double_check_prompts.append(
                f"{GoogleGeminiClient.prompts.agent_machine_job_applicant}"
            )
            double_check_prompts.append(
                f"RESPONSE: {response}"
            )
            double_check_prompts.append(
                f"Respond True or False. Is the RESPONSE following all RULES?"
            )
            double_check, model = run_llm(double_check_prompts)

            if gemini.response_is_false(response):
                ask = prompts_resume + prompts_emails
                ask.append(
                    f"RESPONSE: {response}"
                )
                ask.append(
                    f"say which rule was violated"
                )
                double_check_prompts.append(
                    f"write a prompt to fix what was wrong using the format: \n"
                    f"RULE: reason goes here"
                )
                run_llm(prompts=double_check_prompts, chat=True)

            return double_check, model

        response, model = get_response(thread)

        response_check, model = check_response(response)

        if gemini.reponse_is_true(response_check):
            FAILED = False
            break
        else:
            FAILED = True

    def create_draft():

        if _FOLLOW_UP:
            resume_attachment = []
        else:
            resume_attachment = resume_selected.automon_payload.automon_parts[1]
            assert resume_attachment.filename

            resume_attachment = gmail.v1.EmailAttachment(
                bytes_=resume_attachment.automon_body.automon_data_base64decoded(),
                filename=resume_attachment.filename,
                mimeType=resume_attachment.mimeType)

        to = email_selected.automon_message_first.automon_header_from.value
        from_ = email_selected.automon_message_first.automon_header_to.value

        # create draft
        body = response
        subject = "Re: " + email_selected.automon_message_first.automon_header_subject.value
        if thread.automon_messages_count >= 3:
            draft = gmail.draft_create(
                threadId=email_selected.id,
                draft_to=to,
                draft_from=from_,
                draft_subject=subject,
                draft_body=body,
            )
        else:
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
                              addLabelIds=[labels.unread])

        if (labels.auto_reply_enabled in email_selected.automon_messages_labels
                and labels.sent not in email_selected.automon_message_latest.automon_labels
        ):
            draft_sent = gmail.draft_send(draft=draft)
            gmail.messages_modify(id=email_selected.automon_message_first.id,
                                  addLabelIds=[labels.unread,
                                               labels.waiting])

        gmail.messages_modify(id=email_selected.automon_message_first.id,
                              removeLabelIds=[labels.processing])

    gmail.config.refresh_token()

    if not FAILED:
        create_draft()

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


class MyTestCase(unittest.TestCase):
    def test_something(self):
        while gmail.is_ready():
            main()
        pass


if __name__ == '__main__':
    unittest.main()
