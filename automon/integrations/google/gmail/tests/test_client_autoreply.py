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

# gmail.config.add_gmail_scopes()
gmail.config.add_scopes([
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/gmail.compose",

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

        gemini.add_content(role='model', prompt=gemini.prompts.agent_machine_job_applicant)

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

        ollama.add_message(role='model', content=ollama.prompts.agent_machine_job_applicant)

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


def run_llm(prompts: list) -> (str, any):
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
    _thread = None
    _nextPageToken = None
    while True:

        _FOUND = None
        email_search = gmail.thread_list_automon(
            maxResults=1,
            pageToken=_nextPageToken,
            labelIds=[labels.automon],
        )
        _nextPageToken = email_search.nextPageToken

        for _thread in email_search.threads:

            _first = _thread.automon_message_first
            _latest = _thread.automon_message_latest

            if (labels.retry in _first.automon_labels
                    or labels.retry in _latest.automon_labels):
                _FOUND = True
                break

            if labels.resume in _first.automon_labels:
                continue

            if labels.draft in _latest.automon_labels:
                continue

            if labels.sent in _latest.automon_labels:
                continue

            if _thread:
                _FOUND = True
                break

        if _FOUND:
            break

    resume_search = gmail.messages_list_automon(
        maxResults=1,
        labelIds=[labels.resume]
    )

    if _thread is None or not resume_search:
        try:
            gmail._sleep.seconds(15)
        except KeyboardInterrupt:
            return
        return

    threadId = None

    try:

        # retry
        for _message in _thread.messages:
            _RETRY = False
            if labels.retry in _message.automon_labels:
                _RETRY = True
                gmail.messages_modify(id=_message.id,
                                      removeLabelIds=[labels.retry,
                                                      labels.drafted])

            if _RETRY:
                # delete DRAFT
                if labels.draft in _message.automon_labels:
                    gmail.messages_trash(id=_message.id)

            email_search.threads = [gmail.thread_get_automon(id=_message.threadId)]

        email_selected = _thread
        resume_selected = resume_search.messages[0]

        threadId = email_selected.id

        resume = resume_selected.automon_attachments().attachments[0].body.automon_data_html_text
        resume_attachment = resume_selected.automon_attachments().with_filename()[0]
        resume_attachment = gmail.v1.EmailAttachment(bytes_=resume_attachment.body.automon_data_base64decoded(),
                                                     filename=resume_attachment.filename,
                                                     mimeType=resume_attachment.mimeType)

        to = email_selected.automon_message_first.automon_from().get('value')
        from_ = email_selected.automon_message_first.automon_to().get('value')

        prompts_base = []
        prompts_resume = [f"This is a resume: <RESUME>{resume}</RESUME>\n\n", ]

        i = 1
        prompts_emails = []
        for message in email_selected.messages:
            prompts_emails.append(
                f"This is email {i} in an email chain: {message.to_dict()}\n\n"
            )
            i += 1

        prompts = []
        prompts.extend(prompts_resume)
        prompts.extend(prompts_emails)
        prompts.append(
            f"0. If the rules are not followed, keep thinking until all rules are satisfied. "
            f"\n\n"
            f"1. EXCLUDE emails that have the labels 'TRASH' or 'DRAFT'. "
            f"\n\n"
            f"2. Rules for writing an email reply: "
            f"EXCLUDE the reply if last email is not from the sender of the first email. "
            f"EXCLUDE any subject line. "
            f"EXCLUDE any internal thought process. "
            f"Must write in plain english. "
            f"Must write in first person. "
            f"Provide only the body of the email. "
            f"\n\n"
            f"3. Rules if an email contains the label name `automon/bad`: "
            f"INCLUDE the the first line with 'Rule Violated'"
            f"INCLUDE which rule was violated and provide evidence. "
        )

        print([len(x) for x in prompts])

        response, model = run_llm(prompts=prompts)
        # model.chat_forever()

        gmail.config.refresh_token()

        raw = response

        prompts = prompts_emails.copy()
        prompts.append(
            f"Respond only yes or no, is the job relevant?"
        )
        response, model = run_llm(prompts)
        relevant = response.lower()

        if 'yes' in relevant:
            gmail.messages_modify(id=email_selected.id, addLabelIds=[labels.relevant])

        prompts = prompts_emails.copy()
        prompts.append(
            f"Respond only yes or no, is the job remote?"
        )
        response, model = run_llm(prompts)
        remote = response.lower()

        if 'yes' in remote:
            gmail.messages_modify(id=email_selected.id, addLabelIds=[labels.remote])

        subject = "Re: " + email_selected.automon_message_first.automon_subject().value

        body = raw

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
            f"Respond only yes or no, does any of the emails have the 'auto reply enabled' label name?"
        )
        response, model = run_llm(prompts)
        auto_send = response.lower()

        if 'yes' in auto_send:
            draft_sent = gmail.draft_send(draft=draft)

        gmail.config.refresh_token()

    except Exception as error:
        email_error = 'naisanza@gmail.com'

        bug_report = (f"A error has occurred. \n\n"
                      f"<error>"
                      f"\n{error}\n"
                      f"</error>"
                      f"\n\n"
                      f"If you would like to submit this bug report. "
                      f"Feel free to send this to {email_error}. ")

        gmail.draft_create(threadId=email_selected.id,
                           draft_body=bug_report,
                           draft_subject=f"Bug Report",
                           draft_to=[email_error])
        gmail.messages_modify(id=email_selected.id, addLabelIds=[labels.error,
                                                                 labels.unread,
                                                                 ])

        import traceback
        traceback.print_exc()
        return


class MyTestCase(unittest.TestCase):
    def test_something(self):

        if not gmail.is_ready():
            return

        while True:
            main()
        pass


if __name__ == '__main__':
    unittest.main()
