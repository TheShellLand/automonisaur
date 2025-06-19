import unittest

import datetime
import dateutil.parser

import automon.integrations.google.gmail.v1
from automon.integrations.google.gmail import GoogleGmailClient
from automon import LoggingClient, ERROR, DEBUG, CRITICAL, INFO
from automon.integrations.ollamaWrapper import OllamaClient
from automon.integrations.google.gemini import GoogleGeminiClient

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

gmail = GoogleGmailClient()
gemini = GoogleGeminiClient()

# gmail.config.add_gmail_scopes()
gmail.config.add_scopes([
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
])

if gmail.is_ready():

    # create labels
    labels = gmail._automon_labels
    labels._reset_labels = True

    for key, label in labels.labels.items():
        _get_label = getattr(labels, key)

        _id = _get_label.id
        _name = _get_label.name
        _color = _get_label.color

        if _get_label.id is None:
            _labels_get_by_name = gmail.labels_get_by_name(_name)

            if _labels_get_by_name is None:
                _get_label.update_dict(
                    gmail.labels_create(
                        name=_name,
                        color=_color,
                    )
                )
            else:
                if labels._reset_labels:
                    gmail.labels_update(id=_labels_get_by_name.id, color=_color)

                _get_label.update_dict(
                    _labels_get_by_name
                )

    all_labels = labels.all_labels

MODEL_ERRORS = {}


def run_gemini(prompts: list) -> (str, GoogleGeminiClient):
    gemini = GoogleGeminiClient()
    ollama = OllamaClient()

    free_models = [
        gemini.models.gemini_2_5_flash_preview_05_20,
        # gemini.models.gemini_2_5_flash_preview_tts,
        # gemini.models.gemini_2_5_flash_exp_native_audio_thinking_dialog,
        # gemini.models.gemini_2_5_pro_preview_05_06,
        # gemini.models.gemini_2_5_pro_preview_tts,
        # gemini.models.gemini_2_5_pro_exp_03_25,
        gemini.models.gemini_2_0_flash,
        # gemini.models.gemini_2_0_flash_lite,
        # gemini.models.gemini_2_0_flash_thinking_exp_01_21,
        # gemini.models.gemini_2_0_pro_exp_02_05,
        # gemini.models.gemini_1_5_flash,
        # gemini.models.gemini_1_5_pro,
    ]

    import random
    pick_a_model = random.choice(free_models)
    gemini.set_model(pick_a_model)

    print(f'{MODEL_ERRORS=}')

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
            print(f'[run_gemini] :: ERROR :: {error=}')

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
    print(f'[run_llm] :: {[f"{x:,}" for x in _tokens]} :: {sum(_tokens):,f} tokens')

    while True:
        try:
            if USE_OLLAMA:
                response, model = run_ollama(prompts=prompts)
                break

            if USE_GEMINI:
                response, model = run_gemini(prompts=prompts)
                break
        except Exception as error:
            print(error)

    if response is None:
        raise Exception(f"missing llm response")

    return response, model


def clean_drafts(thread: automon.integrations.google.gmail.v1.Thread):
    for message in thread.messages:
        delete_draft(message)


def is_analyze(thread: automon.integrations.google.gmail.v1.Thread) -> bool:
    for message in thread.messages:
        if labels.analyze in message.automon_labels:
            return True
    return False


def is_auto_reply(thread: automon.integrations.google.gmail.v1.Thread) -> bool:
    for message in thread.messages:
        if labels.auto_reply_enabled in message.automon_labels:
            return True
    return False


def is_draft(message: automon.integrations.google.gmail.v1.Message) -> bool:
    if labels.draft in message.automon_labels:
        return True
    return False


def is_debug(thread: automon.integrations.google.gmail.v1.Thread) -> bool:
    for message in thread.messages:
        if labels.debug in message.automon_labels:
            return True
    return False


def is_resume(thread: automon.integrations.google.gmail.v1.Thread) -> bool:
    for message in thread.messages:
        if labels.resume in message.automon_labels:
            return True
    return False


def is_sent(message: automon.integrations.google.gmail.v1.Message) -> bool:
    if labels.sent in message.automon_labels:
        return True
    return False


def mark_processing(thread: automon.integrations.google.gmail.v1.Thread):
    return gmail.messages_modify(
        id=thread.automon_clean_thread_latest.id,
        addLabelIds=[labels.processing]
    )


def unmark_processing(thread: automon.integrations.google.gmail.v1.Thread):
    return gmail.messages_modify(
        id=thread.automon_clean_thread_latest.id,
        removeLabelIds=[labels.processing]
    )


def not_draft_and_trash(message: automon.integrations.google.gmail.v1.Message) -> bool:
    if labels.draft not in message.automon_labels and labels.trash not in message.automon_labels:
        return True
    return False


def needs_followup(
        thread: automon.integrations.google.gmail.v1.Thread,
        days: int = 3
) -> bool:
    message = thread.automon_clean_thread_latest

    if labels.sent in message.automon_labels:

        latest_date = dateutil.parser.parse(message.payload.get_header('Date').value)
        now = datetime.datetime.now()
        time_delta = ((now + latest_date.utcoffset()).replace(
            tzinfo=datetime.timezone(latest_date.utcoffset())) - latest_date)

        if time_delta.days <= 0:
            time_delta_check = f'last sent {round(time_delta.seconds / 60 / 60)} hours ago'
        else:
            time_delta_check = f'last sent {time_delta.days} days ago'

        print(f' :: {time_delta_check}', end='')

        if time_delta.days >= days:
            print(' :: FOLLOW UP', end='')
            return True

    return False


def delete_draft(message: automon.integrations.google.gmail.v1.Message):
    # delete DRAFT
    if labels.draft in message.automon_labels:
        return gmail.messages_trash(id=message.id)


def main():
    global gemini

    # init
    _welcome_email = gmail.messages_list_automon(labelIds=[labels.automon,
                                                           labels.welcome])

    if _welcome_email.messages:
        delete_draft(_welcome_email.messages[0].id)

    thread = None
    _nextPageToken = None

    _NEW = None
    _FOLLOW_UP = None
    while gmail.is_ready():

        _NEW = None
        _FOLLOW_UP = None
        email_search = gmail.thread_list_automon(
            maxResults=1,
            pageToken=_nextPageToken,
            labelIds=[labels.automon],
        )
        _nextPageToken = email_search.nextPageToken

        if not email_search.threads:
            print('NO THREADS', end='')
            continue

        for thread in email_search.threads:

            # thread = gmail.thread_get_automon('1974178c0bf898af')

            _clean_thread = thread.automon_clean_thread
            _clean_thread_first = thread.automon_clean_thread_first
            _clean_thread_latest = thread.automon_clean_thread_latest

            _first = thread.automon_message_first
            _latest = thread.automon_message_latest

            print(f"{thread.id} :: {_first.payload.get_header('subject')} :: {_first.automon_labels}", end='')

            mark_processing(thread)

            # resume
            if is_resume(thread):
                unmark_processing(thread)
                continue

            if _clean_thread_latest is None:
                unmark_processing(thread)
                continue

            # clean_drafts(thread)

            # needs followup
            if needs_followup(thread):
                _NEW = True
                _FOLLOW_UP = True
                gmail.messages_modify(
                    id=_clean_thread_latest.id,
                    removeLabelIds=[labels.waiting])
                break
            else:
                gmail.messages_modify(id=_clean_thread_latest.id,
                                      addLabelIds=[labels.waiting])

            # analyze
            if is_analyze(thread):
                _NEW = True
                print(' :: ANALYZE', end='')
                break

            # already sent
            if is_sent(_clean_thread_latest):
                unmark_processing(thread)
                continue

            # auto reply
            if is_auto_reply(thread):
                if not is_sent(_clean_thread_latest):
                    if not is_draft(_clean_thread_latest):
                        _NEW = True
                        print(' :: AUTO', end='')
                        break

            # clean drafts
            clean_drafts(thread)

            unmark_processing(thread)
            continue

        if _NEW:
            print(' :: FOUND')
            break

        unmark_processing(thread)
        print("\n")

    try:
        resume_search = gmail.messages_list_automon(
            maxResults=100,
            labelIds=[labels.resume]
        )

        resume_selected = resume_search.messages[0]
        resume_attachments = resume_selected.automon_attachments().attachments
        resume = resume_attachments[0].parts[0].body.automon_data_html_text

    except Exception as error:
        resume_error = gmail.draft_create(
            draft_subject='resume missing',
            draft_to=gmail._userId,
            draft_body=f'Please copy and paste your resume here, and also add it as an attachment.',
        )
        gmail.messages_modify(
            id=resume_error.id,
            addLabelIds=[labels.automon, labels.error, labels.resume]
        )

    try:

        email_selected = thread
        _clean_thread = thread.automon_clean_thread

        to = email_selected.automon_message_first.automon_from().get('value')
        from_ = email_selected.automon_message_first.automon_to().get('value')

        prompts_base = []
        prompts_resume = [f"This is a resume: <RESUME>{resume}</RESUME>\n\n", ]

        i = 1
        prompts_emails = []
        prompts_emails_all = []
        for message in email_selected.messages:

            if is_draft(message):
                continue

            _message = f"{message.to_dict()}"

            import re

            _del = re.compile(r"'data': ('[a-zA-Z0-9-_=]+')").findall(_message)
            for _x in _del:
                _message = _message.replace(_x, "''")

            if not is_draft(message):
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

        # analyze
        if is_analyze(_clean_thread):

            _prompts_email_thread = []

            for _message in _clean_thread.messages:
                _prompts_email_thread.append(
                    _message.automon_attachments().attachments[0].body.automon_data_html_text
                )

            prompts = _prompts_email_thread + [f"Give me an analysis of the email thread. \n"]
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

            if is_debug(email_selected):
                response, model = run_llm(prompts=prompts, chat=True)
            else:
                response, model = run_llm(prompts=prompts, chat=False)

        gmail.config.refresh_token()

        if _FOLLOW_UP:
            resume_attachment = []
        else:
            resume_attachment = resume_selected.automon_attachments().with_filename()[0]
            resume_attachment = gmail.v1.EmailAttachment(bytes_=resume_attachment.body.automon_data_base64decoded(),
                                                         filename=resume_attachment.filename,
                                                         mimeType=resume_attachment.mimeType)

        # create draft
        body = response
        subject = "Re: " + email_selected.automon_message_first.automon_subject().value
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

        if (labels.auto_reply_enabled in email_selected.automon_message_latest.automon_labels
                and labels.sent not in email_selected.automon_message_latest.automon_labels
        ):
            draft_sent = gmail.draft_send(draft=draft)
            gmail.messages_modify(id=email_selected.automon_message_first.id,
                                  addLabelIds=[labels.unread])

        prompts = [prompts_emails[0]] + prompts_resume
        prompts.append(
            f"Respond only true or false, is the job relevant?"
        )
        response, model = run_llm(prompts)
        if gemini.true_or_false(response):
            gmail.messages_modify(id=email_selected.id, addLabelIds=[labels.relevant])

        prompts = [prompts_emails[0]]
        prompts.append(
            f"Respond only true or false, is the job fully and completely remote, with no in-office days?"
        )
        response, model = run_llm(prompts)
        if gemini.true_or_false(response):
            gmail.messages_modify(id=email_selected.id, addLabelIds=[labels.remote])

        CHAT_ONCE = 0

        unmark_processing(thread)


    except Exception as error:

        unmark_processing(thread)
        gmail.config.refresh_token()

        import traceback
        traceback.print_exc()
        return


class MyTestCase(unittest.TestCase):
    def test_something(self):
        while gmail.is_ready():
            main()
        pass


if __name__ == '__main__':
    unittest.main()
