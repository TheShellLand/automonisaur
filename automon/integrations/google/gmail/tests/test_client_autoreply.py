import unittest

import time
import threading
# from idlelib.rpc import response_queue

from automon.integrations.google.gmail import GoogleGmailClient
from automon.integrations.ollamaWrapper import OllamaClient
from automon.integrations.google.gemini import GoogleGeminiClient
from automon import LoggingClient, ERROR, DEBUG, CRITICAL, INFO, debug

DEBUG_LEVEL = 2
DEBUG_ = True
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
LoggingClient.logging.getLogger('automon.helpers.threadingWrapper.client').setLevel(DEFAULT_LEVEL)
LoggingClient.logging.getLogger('opentelemetry.instrumentation.instrumentor').setLevel(DEFAULT_LEVEL)

if DEBUG_:
    LoggingClient.logging.getLogger('automon.integrations.google.gemini.client').setLevel(DEBUG)
    LoggingClient.logging.getLogger('automon.integrations.google.gmail.client').setLevel(DEBUG)
else:
    LoggingClient.logging.getLogger('automon.integrations.google.gemini.client').setLevel(INFO)
    LoggingClient.logging.getLogger('automon.integrations.google.gmail.client').setLevel(INFO)

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

                debug(f"[run_llm] :: ERROR :: {MODEL_ERRORS}")

    if not response:
        raise Exception(f"[run_llm] :: ERROR :: missing llm response :: {response=}")

    return response, model


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

    while gmail.is_ready():

        query_sequence = [
            [labels.automon, labels.error],
            [labels.automon, labels.processing],
            [labels.automon, labels.chat],
            [labels.automon, labels.analyze],
            [labels.automon],
        ]

        def search_email(query, pageToken):
            return gmail.thread_list_automon(
                maxResults=1,
                pageToken=pageToken,
                labelIds=query,
            )

        def email_found(thread):

            # thread = gmail.thread_get_automon(thread.id)

            first = thread.automon_message_first
            latest_clean = thread.automon_clean_thread_latest

            debug(f"{latest_clean.automon_date_since_now_str} :: "
                  f"{thread.automon_messages_count} messages :: "
                  f"{thread.id} :: "
                  f"{first.automon_payload.get_header('subject')} :: ",
                  end='', level=2)

            # resume
            if GoogleGmailClient.utils.is_resume(thread):
                return False

            # chat
            if GoogleGmailClient.utils.is_chat(thread):
                return True

            # skipped
            if GoogleGmailClient.utils.is_skipped(thread):
                return False

            # error
            if GoogleGmailClient.utils.is_error(thread):
                return True

            # analyze
            if GoogleGmailClient.utils.is_analyze(thread):
                return True

            # scheduled
            if GoogleGmailClient.utils.is_scheduled(thread):
                return False

            # sent
            if GoogleGmailClient.utils.is_sent(thread):
                if GoogleGmailClient.utils.is_old(thread):
                    return True
                debug('sent')

            # new
            if GoogleGmailClient.utils.is_new(thread):
                return True

            return False

        _thread_search = None
        _nextPageToken = None
        while not thread_selected:

            for _query in query_sequence:
                _thread_search = search_email(_query, _nextPageToken)

                if _thread_search:
                    for thread in _thread_search.automon_threads:

                        gmail.thread_modify(id=thread.id, addLabelIds=[labels.processing])

                        if email_found(thread):
                            thread_selected = thread
                            break

                        gmail.thread_modify(id=thread.id, removeLabelIds=[labels.processing])

                    if thread_selected: break

                if thread_selected: break

            _nextPageToken = _thread_search.nextPageToken

        if thread_selected: break

    resume_search = gmail.messages_list_automon(
        maxResults=1,
        labelIds=[labels.automon, labels.resume]
    )

    for message in thread.automon_messages:

        # delete DRAFT
        if labels.draft in message.automon_labels:
            gmail.messages_trash(id=message.id)

    resume_selected = resume_search.automon_messages[0]

    resume = resume_selected.automon_attachments_first
    resume = resume.automon_parts[0].automon_body.automon_data_html_text

    prompts_resume = [f"This is your resume: <RESUME>{resume}</RESUME>\n\n", ]

    i = 1
    prompts_emails = []
    prompts_emails_all = []
    for message in thread_selected.automon_messages:

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
    for message in thread_selected.automon_messages:
        if labels.analyze in message.automon_labels:
            if labels.sent in thread_selected.automon_message_latest.automon_labels:
                break

            _draft = thread_selected.automon_message_latest
            _resume = _draft.automon_attachments_first.automon_body.automon_data_html_text

            prompts = [_resume] + [f"Give me an analysis of the resume. \n"]
            response, model = run_llm(prompts=prompts, chat=False)

            gmail.messages_modify(id=_draft.id, removeLabelIds=[labels.analyze])
            gmail.messages_trash(id=_draft.id)
            break

    response_check = False
    while not response_check:

        def is_human(prompts: list) -> bool:
            prompts_check = prompts + GoogleGeminiClient.prompts.TrueOrFalseTemplates().email_is_human
            response, model = run_llm(prompts=prompts_check, chat=False)
            return gemini.reponse_is_true(response)

        def is_rejected_email(prompts: list) -> bool:
            prompts_check = prompts
            prompts_check += GoogleGeminiClient.prompts.TrueOrFalseTemplates().email_is_rejected

            response, model = run_llm(prompts=prompts_check, chat=False)
            return gemini.reponse_is_true(response)

        def get_response(prompts: list) -> tuple[str, any]:
            prompts_ask = prompts + [GoogleGeminiClient.prompts.AgentTemplates().agent_machine_job_applicant]

            chat = False

            if labels.error in thread_selected.automon_messages_labels:
                chat = True

            if labels.chat in thread_selected.automon_messages_labels:
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

        if is_human(prompts):
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

    def draft_create(thread):

        if GoogleGmailClient.utils.is_follow_up(thread):
            resume_attachment = []

        if not GoogleGmailClient.utils.has_doc_attachment(thread):
            resume_attachment = resume_selected.automon_attachments[1]
            assert resume_attachment.filename

            resume_attachment = gmail.classes.EmailAttachment(
                bytes_=resume_attachment.automon_body.automon_data_base64decoded(),
                filename=resume_attachment.filename,
                mimeType=resume_attachment.mimeType)

        to = thread.automon_message_first.automon_header_from.value
        from_ = thread.automon_message_first.automon_header_to.value

        # create draft
        body = response
        subject = "Re: " + thread_selected.automon_message_first.automon_header_subject.value
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

    def draft_send(draft):
        draft_sent = gmail.draft_send(draft=draft)
        gmail.messages_modify(
            id=thread_selected.automon_message_first.id,
            addLabelIds=[labels.unread])
        return draft_sent

    gmail.config.refresh_token()

    if not GoogleGmailClient.utils.is_skipped(thread_selected):
        if GoogleGmailClient.utils.is_follow_up(thread_selected):
            draft = draft_create(thread_selected)
            draft_send(draft=draft)

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
