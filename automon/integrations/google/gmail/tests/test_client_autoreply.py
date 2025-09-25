import unittest

import re
import datetime
import dateutil.parser

from automon.helpers import *
import automon.integrations.google.gmail.v1
from automon.integrations.google.gmail import GoogleGmailClient
from automon import LoggingClient, ERROR, DEBUG, CRITICAL, INFO
from automon.integrations.ollamaWrapper import OllamaClient
from automon.integrations.google.gemini import GoogleGeminiClient
from automon.integrations.google.gmail.automon_gmail import AutomonGmailClient

DEBUG_ = True
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

USE_OLLAMA = False
USE_GEMINI = True
CHAT_FOREVER = False

automon_gmail = AutomonGmailClient()
gemini = GoogleGeminiClient()

# gmail.config.add_gmail_scopes()
automon_gmail.config.add_scopes([
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
])

if automon_gmail.is_ready():
    automon_gmail.create_labels()

MODEL_ERRORS = {}


def run_gemini(prompts: list) -> (str, GoogleGeminiClient):
    gemini = GoogleGeminiClient()
    ollama = OllamaClient()

    pick_a_model = gemini.pick_random_free_model()
    gemini.set_model(pick_a_model)

    debug(f'[*] [run_gemini] :: {MODEL_ERRORS=}')

    if gemini.is_ready():

        # gemini.add_content(role='model', prompt=gemini.prompts.agent_machine_job_applicant)

        for prompt in prompts:
            gemini.add_content(prompt)

        try:
            if CHAT_FOREVER:
                gemini_response = gemini.chat().chat_forever().chat_response()
            else:
                gemini_response = gemini.chat().chat_response()
            return gemini_response, gemini
        except Exception as error:
            debug(f'[*] [run_gemini] :: ERROR :: {error=}')

            # global MODEL_ERRORS
            if pick_a_model in MODEL_ERRORS.keys():
                MODEL_ERRORS[pick_a_model] += 1
            else:
                MODEL_ERRORS[pick_a_model] = 1

            return run_gemini(prompts)


def run_ollama(prompts: list) -> (str, OllamaClient):
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


def run_llm(prompts: list, chat: bool = False) -> (str, any):
    global CHAT_FOREVER
    CHAT_FOREVER = chat

    _tokens = [len(x) for x in prompts]
    debug(f'[*] [run_llm] :: {[f"{x:,}" for x in _tokens]} :: {sum(_tokens):,} tokens')

    while True:
        try:
            if USE_OLLAMA:
                response, model = run_ollama(prompts=prompts)
                break

            if USE_GEMINI:
                response, model = run_gemini(prompts=prompts)
                break
        except Exception as error:
            debug(error)

    if response is None:
        raise Exception(f"missing llm response")

    return response, model


def main():
    global gemini

    labels = automon_gmail.labels

    # init
    _welcome_email = automon_gmail.messages_list_automon(labelIds=[labels.automon,
                                                                   labels.welcome])

    if _welcome_email.messages:
        automon_gmail.delete_draft(_welcome_email.messages[0].id)

    thread = None
    _nextPageToken = None

    _FOUND = None
    while automon_gmail.is_ready():

        _FOUND = None
        email_search = automon_gmail.thread_list_automon(
            maxResults=1,
            pageToken=_nextPageToken,
            labelIds=[labels.automon],
        )
        _nextPageToken = email_search.nextPageToken

        if not email_search.threads:
            debug('NO THREADS')
            continue

        for thread in email_search.threads:

            # thread = gmail.thread_get_automon('1974178c0bf898af')

            _clean_thread = thread.automon_clean_thread
            _clean_thread_first = thread.automon_clean_thread_first
            _clean_thread_latest = thread.automon_clean_thread_latest

            _first = thread.automon_message_first
            _latest = thread.automon_message_latest

            debug(f"[*] {thread.id} :: {_first.payload.get_header('subject')} :: {_first.automon_labels}")

            automon_gmail.mark_processing(thread)

            # resume
            if automon_gmail.is_resume(thread):
                automon_gmail.unmark_processing(thread)
                continue

            # chat
            if automon_gmail.is_chat(thread):
                _FOUND = True
                debug(f'[*] {thread} :: CHAT')
                break

            # needs followup
            if automon_gmail.needs_followup(thread):
                _FOUND = True
                automon_gmail.messages_modify(
                    id=_clean_thread_latest.id,
                    removeLabelIds=[labels.waiting])
                break
            else:
                automon_gmail.messages_modify(id=_clean_thread_latest.id,
                                              addLabelIds=[labels.waiting])

            # analyze
            if automon_gmail.is_analyze(thread):
                _FOUND = True
                debug(f'[*] {thread} :: ANALYZE')
                break

            # already sent
            if automon_gmail.is_sent(_clean_thread_latest):
                automon_gmail.unmark_processing(thread)
                continue

            # auto reply
            if automon_gmail.is_auto_reply(thread):
                if not automon_gmail.is_sent(_clean_thread_latest):
                    if not automon_gmail.is_draft(_clean_thread_latest):
                        _FOUND = True
                        debug(f'[*] {thread} :: AUTO')
                        break

            # clean drafts
            automon_gmail.clean_drafts(thread)

            automon_gmail.unmark_processing(thread)
            continue

        if _FOUND:
            debug(f'[*] {thread} :: FOUND')
            break

        automon_gmail.unmark_processing(thread)
        debug("\n")

    try:
        resume_search = automon_gmail.messages_list_automon(
            maxResults=100,
            labelIds=[labels.resume]
        )

        resume_selected = resume_search.messages[0]
        resume_attachments = resume_selected.automon_attachments.attachments
        resume = resume_attachments[0].parts[0].body.automon_data_html_text

    except Exception as error:
        resume_error = automon_gmail.draft_create(
            draft_subject='resume missing',
            draft_to=automon_gmail._userId,
            draft_body=f'Please copy and paste your resume here, and also add it as an attachment.',
        )
        automon_gmail.messages_modify(
            id=resume_error.id,
            addLabelIds=[labels.automon, labels.error, labels.resume]
        )

        raise Exception(f'failed to get resume :: ERROR :: {error=}')

    try:

        email_selected = thread
        _clean_thread = thread.automon_clean_thread

        to = email_selected.automon_message_first.automon_from().get('value')
        from_ = email_selected.automon_message_first.automon_to().get('value')

        prompts_base = []
        prompts_resume = [f"This is a resume: <RESUME>{resume}</RESUME>\n\n", ]

        i = 1
        prompts_emails = []
        for message in email_selected.automon_full_thread.messages:
            _message = automon_gmail.delete_extra_data(message)

            prompts_emails.append(
                f"This is email {i} in an email chain: {_message}\n\n"
            )

            i += 1

        if not prompts_emails:
            raise Exception(f'prompts_emails list is empty')

        response = None

        # analyze
        if automon_gmail.is_analyze(_clean_thread):
            prompts = prompts_emails + [f"Give me an analysis of the email thread. \n"]
            response, model = run_llm(prompts=prompts, chat=False)

        # chat
        if automon_gmail.is_chat(email_selected):
            prompts = prompts_emails
            response, model = run_llm(prompts=prompts, chat=False)

        if response is None:
            prompts = prompts_resume + prompts_emails
            prompts.append(
                GoogleGeminiClient.prompts.agent_machine_job_applicant,
            )
            prompts.append(
                f"MUST check for a job description in the first email before continuing. \n"
                f"\n\n"
                f"Create a response. "
            )

            if automon_gmail.is_debug(email_selected):
                response, model = run_llm(prompts=prompts, chat=True)
            else:
                response, model = run_llm(prompts=prompts, chat=False)

        automon_gmail.config.refresh_token()

        if automon_gmail.needs_followup(email_selected):
            resume_attachment = []
        else:
            resume_attachment = resume_selected.automon_attachments.with_filename()[0]
            resume_attachment = automon_gmail.v1.EmailAttachment(
                bytes_=resume_attachment.body.automon_data_base64decoded(),
                filename=resume_attachment.filename,
                mimeType=resume_attachment.mimeType)

        # create draft
        body = response
        subject = "Re: " + email_selected.automon_message_first.automon_subject.value
        draft = automon_gmail.draft_create(
            threadId=email_selected.id,
            draft_to=to,
            draft_from=from_,
            draft_subject=subject,
            draft_body=body,
            draft_attachments=[resume_attachment]
        )
        draft_get = automon_gmail.draft_get_automon(id=draft.id)

        automon_gmail.messages_modify(id=email_selected.id,
                                      addLabelIds=[labels.unread])

        if (labels.auto_reply_enabled in email_selected.automon_message_latest.automon_labels
                and labels.sent not in email_selected.automon_message_latest.automon_labels
        ):
            draft_sent = automon_gmail.draft_send(draft=draft)
            automon_gmail.messages_modify(id=email_selected.automon_message_first.id,
                                          addLabelIds=[labels.unread])

        prompts = [prompts_emails[0]] + prompts_resume
        prompts.append(
            f"Respond only true or false, is the job relevant?"
        )
        response, model = run_llm(prompts)
        if gemini.true_or_false(response):
            automon_gmail.messages_modify(id=email_selected.id, addLabelIds=[labels.relevant])

        prompts = [prompts_emails[0]]
        prompts.append(
            f"Respond only true or false, is the job fully and completely remote, with no in-office days?"
        )
        response, model = run_llm(prompts)
        if gemini.true_or_false(response):
            automon_gmail.messages_modify(id=email_selected.id, addLabelIds=[labels.remote])

        CHAT_ONCE = 0

        automon_gmail.unmark_processing(thread)


    except Exception as error:

        automon_gmail.unmark_processing(thread)
        automon_gmail.config.refresh_token()

        import traceback
        traceback.print_exc()
        raise


class MyTestCase(unittest.TestCase):
    def test_something(self):
        while automon_gmail.is_ready():
            main()
        pass


if __name__ == '__main__':
    unittest.main()
