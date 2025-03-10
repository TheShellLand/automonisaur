import unittest

from automon.integrations.google.gmail import GoogleGmailClient
from automon import LoggingClient, ERROR, DEBUG
from automon.integrations.ollamaWrapper import OllamaClient

LoggingClient.logging.getLogger('httpx').setLevel(ERROR)
LoggingClient.logging.getLogger('httpcore').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.client').setLevel(DEBUG)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.utils').setLevel(ERROR)
LoggingClient.logging.getLogger('automon.integrations.ollamaWrapper.chat').setLevel(ERROR)
LoggingClient.logging.getLogger('opentelemetry.instrumentation.instrumentor').setLevel(ERROR)


class MyTestCase(unittest.TestCase):
    def test_something(self):
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

            gmail.labels_update(id=label_automon.id, color=color)
            gmail.labels_update(id=label_processed.id, color=color)
            gmail.labels_update(id=label_drafted.id, color=color)
            gmail.labels_update(id=label_reviewed.id, color=color)
            gmail.labels_update(id=label_resume.id, color=color)
            gmail.labels_update(id=label_read.id, color=color)

            while True:
                email_search = gmail.messages_list_automon(
                    q=f"label:automon -label:automon/drafted -label:automon/reviewed",
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

                gmail.messages_modify(id=email_selected.id, removeLabelIds=[label_processed.id,
                                                                            label_drafted.id,
                                                                            label_read.id,
                                                                            label_reviewed.id])

                email = email_selected
                threadId = email_selected.threadId
                to = email_selected.automon_sender.value
                from_ = 'ericjaw@gmail.com'

                resume_ollama = resume_selected.automon_attachments.from_hash('f4da226b765738cd8919bcd101e3047e')
                resume_str = resume_ollama.automon_attachment['decoded']

                resume_attachment = resume_selected.automon_attachments.from_hash('6adf97f83acf6453d4a6a4b1070f3754')
                resume_attachment = gmail.v1.EmailAttachment(bytes_=resume_ollama.body.automon_data_base64decoded,
                                                             filename='ERIC JAW RESUME 2025' + '.txt',
                                                             mimeType=resume_ollama.mimeType)

                gmail.messages_modify(id=email_selected.id, addLabelIds=[label_read.id])

                ollama = OllamaClient()
                ollama.add_message(
                    ollama.use_template_chatbot_with_thinking()
                ).add_message(
                    f"Read this email: <EMAIL>{email}</EMAIL>"
                ).add_message(
                    f"Read this resume: <RESUME>{resume_str}</RESUME>"
                ).add_message(
                    f"Tell me how relevant the <RESUME> is with the job description in the <EMAIL>"
                ).add_message(
                    f"Then write me an email reply."
                ).add_message(
                    f"Only give me the body of the email response."
                )
                ollama.set_context_window(ollama.get_total_tokens() * 1.10)
                ollama_response = ollama.chat().chat_response

                import re
                think_re = re.compile(r"(<think>.*</think>)", flags=re.DOTALL)
                think_ = think_re.search(ollama_response).groups()
                think_ = str(think_).strip()

                response_re = re.compile(r"<think>.*</think>(.*)", flags=re.DOTALL)
                response_ = response_re.search(ollama_response).groups()
                response_ = str(response_[0]).strip()

                raw = response_

                gmail.messages_modify(id=threadId, addLabelIds=[label_processed.id])

                subject = None
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

                gmail.messages_modify(id=threadId, addLabelIds=[label_drafted.id])

        pass


if __name__ == '__main__':
    unittest.main()
