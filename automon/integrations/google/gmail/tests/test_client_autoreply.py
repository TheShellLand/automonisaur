import unittest

from automon.integrations.google.gmail import GoogleGmailClient
from automon import LoggingClient, ERROR, DEBUG, CRITICAL, INFO
from automon.integrations.ollamaWrapper import OllamaClient
from automon.integrations.google.gemini import GoogleGeminiClient

LoggingClient.logging.getLogger('httpx').setLevel(ERROR)
LoggingClient.logging.getLogger('httpcore').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.client').setLevel(DEBUG)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.utils').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.chat').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.requestsWrapper.client').setLevel(CRITICAL)
LoggingClient.logging.getLogger('automon.integrations.google.oauth.config').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.google.gemini.client').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.google.gemini.config').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.google.gmail.client').setLevel(ERROR)
LoggingClient.logging.getLogger('opentelemetry.instrumentation.instrumentor').setLevel(ERROR)

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


def run_gemini(prompts: list) -> (str, GoogleGeminiClient):
    gemini = GoogleGeminiClient()
    ollama = OllamaClient()

    free_models = [
        gemini.models.gemini_2_0_flash,
        # gemini.models.gemini_2_0_flash_lite,
        # gemini.models.gemini_2_0_flash_thinking_exp_01_21,
        # gemini.models.gemini_2_0_pro_exp_02_05,
        # gemini.models.gemini_1_5_flash,
        # gemini.models.gemini_1_5_pro,
    ]

    import random
    gemini.set_model(random.choice(free_models))

    if gemini.is_ready():

        # gemini.add_content(role='model', prompt=gemini.prompts.agent_machine_job_applicant)

        for prompt in prompts:
            gemini.add_content(prompt)

        if CHAT_FOREVER:
            gemini_response = gemini.chat().chat_forever().chat_response()
        else:
            gemini_response = gemini.chat().chat_response()
        return gemini_response, gemini


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

    print([f"{len(x):,}" for x in prompts])

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


def main():
    global gemini

    # init
    _welcome_email = gmail.messages_list_automon(labelIds=[labels.automon,
                                                           labels.welcome])

    if _welcome_email.messages:
        gmail.messages_trash(id=_welcome_email.messages[0].id)

    _welcome_body, model = run_llm(prompts=[
        f"Create an HTML format email message for a service that helps you automate "
        f"responding to job recruiter emails. \n"
        f"The service is called TiredofReplying.com. \n"
        f"Everything runs directly from your Gmail inbox. "
        f"It does this by analyzing the recruiter emails and your resume, then it "
        f"creates a personalized email using your relevant job history and "
        f"experience. \n"
        f"And all you have to do is tag an email with the `automon` label. "
        f"The rest is handled automatically. "
        f"\n\n"
        f"MUST Return only the code between <html> code </html>. "
        f"Exclude the code fences (```html and ```) surrounding the HTML code. "
        f"Exclude everything else. "
    ])

    _welcome_email_parts = [gmail.v1.EmailAttachment(
        bytes_=_welcome_body.encode(),
        mimeType=x
    ) for x in ['text/html']]

    _welcome_email = gmail.draft_create(
        draft_subject=f"Welcome to your personal job assistant!",
        draft_attachments=_welcome_email_parts,
    )

    gmail.messages_modify(id=_welcome_email.message.id,
                          addLabelIds=[labels.automon,
                                       labels.welcome])

    # resume check
    # gmail.draft_create(
    #     draft_subject=f""
    # )

    _thread = None
    _nextPageToken = None
    while gmail.is_ready():

        _FOUND = None
        email_search = gmail.thread_list_automon(
            maxResults=1,
            pageToken=_nextPageToken,
            labelIds=[labels.automon],
        )
        _nextPageToken = email_search.nextPageToken

        if not email_search.threads:
            print('_', end='')
            continue

        for _thread in email_search.threads:

            print('.', end='')

            _first = _thread.automon_message_first
            _latest = _thread.automon_message_latest

            if (labels.auto_reply_enabled in _first.automon_labels
                    or labels.auto_reply_enabled in _latest.automon_labels
            ):
                _FOUND = True
                print('auto', end='')
                break

            if (labels.analyze in _first.automon_labels
            ):
                _FOUND = True
                print('analyze', end='')
                break

            if (labels.test in _first.automon_labels
            ):
                _FOUND = True
                print('test', end='')
                break

            if (labels.retry in _first.automon_labels
                    or labels.retry in _latest.automon_labels
            ):
                _FOUND = True
                print('retry', end='')
                break

            if _first.automon_from_email().lower() == _latest.automon_from_email().lower():
                _FOUND = True
                print('new', end='')
                break

            if labels.resume in _first.automon_labels:
                continue

            if labels.draft in _latest.automon_labels:
                continue

            if labels.sent in _latest.automon_labels:
                continue

        if _FOUND:
            print(' :)')
            break

    resume_search = gmail.messages_list_automon(
        maxResults=1,
        labelIds=[labels.resume]
    )

    try:

        # retry
        for _message in _thread.messages:
            _RETRY = False
            if (
                    labels.retry in _message.automon_labels
                    or labels.auto_reply_enabled in _message.automon_labels
            ):
                _RETRY = True
                gmail.messages_modify(id=_message.id,
                                      removeLabelIds=[labels.retry,
                                                      labels.drafted])

                # delete DRAFT
                if labels.draft in _message.automon_labels:
                    gmail.messages_trash(id=_message.id)

            email_search.threads = [gmail.thread_get_automon(id=_message.threadId)]

        global email_selected
        email_selected = _thread
        resume_selected = resume_search.messages[0]

        resume = resume_selected.automon_attachments().attachments[0].body.automon_data_html_text

        to = email_selected.automon_message_first.automon_from().get('value')
        from_ = email_selected.automon_message_first.automon_to().get('value')

        prompts_base = []
        prompts_resume = [f"This is a resume: <RESUME>{resume}</RESUME>\n\n", ]

        i = 1
        prompts_emails = []
        prompts_emails_all = []
        for message in email_selected.messages:

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
        for _message in email_selected.messages:
            if labels.analyze in _message.automon_labels:
                if labels.sent in email_selected.automon_message_latest.automon_labels:
                    break

                _draft = email_selected.automon_message_latest
                _resume = _draft.automon_attachments().attachments[0].body.automon_data_html_text
                prompts = [_resume] + [f"Give me an analysis of the resume. \n"]
                response, model = run_llm(prompts=prompts, chat=True)
                gmail.messages_modify(id=_draft.id, removeLabelIds=[labels.analyze])
                gmail.messages_trash(id=_draft.id)
                break

        if response is None:
            prompts = prompts_resume + prompts_emails
            prompts.append(
                GoogleGeminiClient.prompts.agent_machine_job_applicant,
            )
            prompts.append(
                f"MUST NOT have a reply if last email is not from the sender of the first email. \n"
                f"EXCLUDE any email subject line. \n"
                f"EXCLUDE any internal thought process. \n"
                f"EXCLUDE any chain of thought process. \n"
                f"EXCLUDE any conversational parts. \n"
                f"MUST write in plain english. \n"
                f"MUST write in first person. \n"
                f"MUST respond as if in a conversation. \n"
                f"MUST provide only the body of the response. \n"
                f"MUST check for a job description in the first email before continuing. \n"
                f"\n\n"
                f"Create a response. "
            )
            response, model = run_llm(prompts=prompts, chat=False)

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
                              addLabelIds=[labels.drafted,
                                           labels.unread,
                                           ],
                              )

        prompts = prompts_emails.copy()
        prompts.append(
            f"Respond only true or false, does any of the emails have the 'auto reply enabled' label name?"
        )
        response, model = run_llm(prompts)
        if gemini.true_or_false(response.lower()):
            draft_sent = gmail.draft_send(draft=draft)

        prompts = [prompts_emails[0]] + prompts_resume
        prompts.append(
            f"Respond only true or false, is the job relevant?"
        )
        response, model = run_llm(prompts)
        if gemini.true_or_false(response.lower()):
            gmail.messages_modify(id=email_selected.id, addLabelIds=[labels.relevant])

        prompts = [prompts_emails[0]]
        prompts.append(
            f"Respond only true or false, is the job remote?"
        )
        response, model = run_llm(prompts)
        if gemini.true_or_false(response.lower()):
            gmail.messages_modify(id=email_selected.id, addLabelIds=[labels.remote])

        CHAT_ONCE = 0

    except Exception as error:

        import traceback
        llm_check = [
                        f"Tell me what the error from this stacktrace could be. \n"
                    ] + [str(dict(line=x.line, filename=x.filename)) for x in traceback.extract_stack()]
        response, model = run_llm(llm_check)

        email_error = 'naisanza@gmail.com'

        bug_report = (f"{response}")

        _draft = gmail.draft_create(threadId=email_selected.messages[0].id,
                                    draft_subject=f"Bug Report",
                                    draft_body=bug_report,
                                    draft_to=[email_error])
        gmail.messages_modify(id=_draft.message.id, addLabelIds=[labels.error,
                                                                 labels.unread,
                                                                 ])

        traceback.print_exc()
        return


class MyTestCase(unittest.TestCase):
    def test_something(self):
        while gmail.is_ready():
            main()
        pass


if __name__ == '__main__':
    unittest.main()
