import unittest

from automon.integrations.google.gmail import GoogleGmailClient
from automon import LoggingClient, ERROR, DEBUG, CRITICAL
from automon.integrations.ollamaWrapper import OllamaClient
from automon.integrations.google.gemini import GoogleGeminiClient

LoggingClient.logging.getLogger('httpx').setLevel(ERROR)
LoggingClient.logging.getLogger('httpcore').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.client').setLevel(DEBUG)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.utils').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.chat').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.requestsWrapper.client').setLevel(CRITICAL)
LoggingClient.logging.getLogger('automon.integrations.google.oauth.config').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.google.gemini.config').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.google.gmail.client').setLevel(ERROR)
LoggingClient.logging.getLogger('opentelemetry.instrumentation.instrumentor').setLevel(ERROR)

gmail = GoogleGmailClient()

# gmail.config.add_gmail_scopes()
gmail.config.add_scopes(
    ["https://mail.google.com/"]
)

if gmail.is_ready():
    color = gmail.v1.Color(backgroundColor='#653e9b', textColor='#b694e8')

    gmail.labels_create(name='automon', color=color)
    gmail.labels_create(name='automon/processed', color=color)
    gmail.labels_create(name='automon/drafted', color=color)
    gmail.labels_create(name='automon/reviewed', color=color)
    gmail.labels_create(name='automon/resume', color=color)
    gmail.labels_create(name='automon/read', color=color)

    label_automon = gmail.labels_get_by_name(name='automon')
    label_processed = gmail.labels_get_by_name(name='automon/processed')
    label_drafted = gmail.labels_get_by_name(name='automon/drafted')
    label_reviewed = gmail.labels_get_by_name(name='automon/reviewed')
    label_resume = gmail.labels_get_by_name(name='automon/resume')
    label_read = gmail.labels_get_by_name(name='automon/read')

    all_labels = [
        label_automon,
        label_processed,
        label_drafted,
        label_reviewed,
        label_read,
    ]

    gmail.labels_update(id=label_automon.id, color=color)
    gmail.labels_update(id=label_processed.id, color=color)
    gmail.labels_update(id=label_drafted.id, color=color)
    gmail.labels_update(id=label_reviewed.id, color=color)
    gmail.labels_update(id=label_resume.id, color=color)
    gmail.labels_update(id=label_read.id, color=color)


class MyTestCase(unittest.TestCase):
    def test_something(self):

        USE_OLLAMA = False
        USE_GEMINI = True

        if not gmail.is_ready():
            return

        while True:

            email_search = gmail.messages_list_automon(
                q=f"label:automon -label:automon/drafted -label:automon/reviewed -label:automon/resume",
                maxResults=1,
            )

            resume_search = gmail.messages_list_automon(
                q=f"label:automon/resume",
                maxResults=1,
            )

            # gmail.draft_list_automon(maxResults=5, q="")

            if not email_search or not resume_search:
                gmail._sleep.seconds(5)
                continue

            for _ in email_search.messages:
                email_selected = _
            for _ in resume_search.messages:
                resume_selected = _

            gmail.messages_modify(id=email_selected.id, removeLabelIds=all_labels)

            try:
                email = email_selected.automon_attachment.bs4().html.text
            except:
                try:
                    email = email_selected.automon_attachments.first().automon_attachment.bs4().html.text
                except:
                    try:
                        email = email_selected.automon_attachments.first().automon_attachments.first().automon_attachment.bs4().html.text
                    except:
                        raise Exception(f"email not found")

            threadId = email_selected.threadId
            to = email_selected.automon_sender.value
            from_ = 'ericjaw@gmail.com'

            resume_ollama = resume_selected.automon_attachments.from_hash('f4da226b765738cd8919bcd101e3047e')
            resume_str = resume_ollama.automon_attachment.decoded

            resume_attachment = resume_selected.automon_attachments.from_hash('6adf97f83acf6453d4a6a4b1070f3754')
            resume_attachment = gmail.v1.EmailAttachment(bytes_=resume_ollama.body.automon_data_base64decoded,
                                                         filename='ERIC JAW RESUME 2025' + '.txt',
                                                         mimeType=resume_ollama.mimeType)

            response = None

            prompts = [
                f"This is the email: <EMAIL>{email}</EMAIL>",
                f"This is your resume: <RESUME>{resume_str}</RESUME>",
                f"Answer this question only if the email is not a job description:",
                f"What is this email?",
                f"Answer the following questions only if the email is a job description:",
                f"What's the relevance of the job ot you?",
                f"In a sentence, show me the % the job is relevant to you?",
                f"Furthermore, where can I schedule a call with you?",
                f"Just tell me that your resume is attached in a short sentence."
            ]

            if USE_OLLAMA:
                response, model = run_ollama(prompts=prompts)

            if USE_GEMINI:
                response, model = run_gemini(prompts=prompts)
                # model.chat_forever()

            if response is None:
                raise Exception(f"missing llm response")

            gmail.config.refresh_token()

            raw = response

            import re
            percentage = re.compile(r'\d+%').search(raw)

            if percentage:
                percentage = percentage.group()

                gmail.labels_create(name=f'automon/relevance/{percentage}', color=color)
                label_percentage = gmail.labels_get_by_name(name=f'automon/relevance/{percentage}')
                gmail.labels_update(id=label_percentage.id, color=color)

                gmail.messages_modify(id=threadId, addLabelIds=[label_percentage])

            subject = "Re: " + email_selected.automon_subject.value
            body = raw

            draft = gmail.draft_create(
                threadId=threadId,
                draft_to=to,
                draft_from=from_,
                draft_subject=subject,
                draft_body=body,
                draft_attachments=[resume_attachment]
            )

            draft_get = gmail.messages_get_automon(id=threadId)

            gmail.messages_modify(id=threadId, addLabelIds=[label_drafted])

            gmail.config.refresh_token()

        pass


def run_gemini(prompts: list) -> (str, GoogleGeminiClient):
    gemini = GoogleGeminiClient()
    gemini.set_model(gemini.models.gemini_2_0_flash)

    if gemini.is_ready():

        gemini.add_content(role='model', prompt=f"You are to a person.")
        gemini.add_content(role='model', prompt=f"Assume the experience in the provided resume.")
        gemini.add_content(role='model', prompt=f"Respond with the tone and use of words from the resume.")

        for prompt in prompts:
            gemini.add_content(prompt)

        gemini_response = gemini.chat().chat_response()
        return gemini_response, gemini


def run_ollama(prompts: list) -> (str, OllamaClient):
    ollama = OllamaClient()
    ollama.set_model('deepseek-r1:8b')

    if ollama.is_ready():

        ollama.add_message(role='model', content=f"You are to a person.")
        ollama.add_message(role='model', content=f"Assume the experience in the provided resume.")
        ollama.add_message(role='model', content=f"Respond with the tone and use of words from the resume.")

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


if __name__ == '__main__':
    unittest.main()
