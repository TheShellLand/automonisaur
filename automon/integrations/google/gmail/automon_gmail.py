import re
import datetime
import dateutil.parser
from automon.helpers.threadingWrapper import ThreadingClient

from automon.helpers import *

from .client import (
    GoogleGmailClient,
    GoogleGmailConfig,
    GmailLabels,
    Color,
    Label,
    Thread,
    Message,
)


class AutomonLabels(GmailLabels):

    def __init__(self):
        super().__init__()

        self.reset_labels = False

        # colors
        self._color_default = Color(backgroundColor='#653e9b', textColor='#e4d7f5')

        self._color_green = Color(backgroundColor='#076239', textColor='#b9e4d0')
        self._color_red = Color(backgroundColor='#cc3a21', textColor='#ffd6a2')
        self._color_yellow = Color(backgroundColor='#cf8933', textColor='#ffd6a2')

        self._color_resume = Color(backgroundColor='#b65775', textColor='#ffffff')
        self._color_error = self._color_red
        self._color_enabled = self._color_green
        self._color_welcome = self._color_default
        self._color_waiting = self._color_yellow
        self._color_processing = self._color_yellow

        # required
        self.automon = Label(name='automon', color=self._color_default)

        # allow auto reply
        self.auto_reply_enabled = Label(name='automon/auto reply enabled', color=self._color_default)

        # currently processing
        self.processing = Label(name='automon/processing >>>', color=self._color_processing)

        # welcome
        self.welcome = Label(name='automon/welcome', color=self._color_welcome)
        self.help = Label(name='automon/help', color=self._color_welcome)

        # resume
        self.resume = Label(name='automon/resume', color=self._color_resume)

        # analyze
        self.analyze = Label(name='automon/analyze', color=self._color_default)

        # waiting
        self.waiting = Label(name='automon/waiting', color=self._color_default)

        # skipped
        self.skipped = Label(name='automon/skipped', color=self._color_default)

        # scheduled
        self.scheduled = Label(name='automon/scheduled', color=self._color_enabled)

        # relevance
        self.relevant = Label(name='automon/relevant', color=self._color_default)

        # remote
        self.remote = Label(name='automon/remote', color=self._color_default)

        # need user input
        self.user_action_required = Label(name='automon/user action required', color=self._color_error)

        # debugging
        self.debug = Label(name='automon/debug', color=self._color_error)

        # error
        self.error = Label(name='automon/error', color=self._color_error)

    def all_labels(self):
        return [
            getattr(self, x) for x in dir(self)
            if isinstance(getattr(self, x), Label)
            if getattr(self, x).name.startswith('automon')
        ]


class AutomonGmailClient(GoogleGmailClient):
    _labels = AutomonLabels()

    def __init__(self, config: GoogleGmailConfig = None):
        super().__init__(config)

        self._scopes_automon()

    def _scopes_automon(self):
        scopes = [
            "https://www.googleapis.com/auth/gmail.labels",
            "https://www.googleapis.com/auth/gmail.compose",
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.modify",
        ]
        return self.config.add_gmail_scopes(scopes=scopes)

    def create_labels(self):
        """create all automon labels"""
        labels = self._labels
        labels.reset_labels = True

        def init_automon_labels(label, reset_labels):

            id = label.id
            name = label.name
            color = label.color

            if label.id is None:
                labels_get_by_name = self.labels_get_by_name(name)

                if labels_get_by_name is None:
                    label.automon_update(
                        self.labels_create(
                            name=name,
                            color=color,
                        )
                    )
                else:
                    if reset_labels:
                        self.labels_update(id=labels_get_by_name.id, color=color)

                    label.automon_update(
                        labels_get_by_name
                    )

        threading = ThreadingClient()

        for label in labels.all_labels():
            threading.add_worker(target=init_automon_labels, args=(label, labels.reset_labels))

        return threading.start()

    def clean_drafts(self, thread: Thread):
        for message in thread.messages:
            self.delete_draft(message)

    def delete_draft(self, message: Message):
        # delete DRAFT
        if self._labels.draft in message.labelIds:
            return self.messages_trash(id=message.id)

    def delete_extra_data(self, message: Message):
        message_str = str(message.to_dict())

        delete_regex = r"'data': ('[a-zA-Z0-9-_=]+')"
        delete_list = re.compile(delete_regex).findall(message_str)
        for delete in delete_list:
            message_str = message_str.replace(delete, "''")

        return message_str

    def get_resume_message(self):

        resume_search = self.messages_list_automon(
            maxResults=100,
            labelIds=[self._labels.resume]
        )

        resume_selected = resume_search.messages[0]

        if resume_selected:
            return resume_selected

        resume_error = self.draft_create(
            draft_subject='resume missing',
            draft_to=self._userId,
            draft_body=f'Please copy and paste your resume here, and also add it as an attachment.',
        )

        self.messages_modify_automon(
            id=resume_error.id,
            addLabelIds=[self._labels.automon, self._labels.error, self._labels.resume]
        )
        raise Exception(f'[ERROR] :: {resume_error}')

    def get_resume_text(self):

        resume_selected = self.get_resume_message()

        resume_attachments = resume_selected._attachments_first
        resume = resume_attachments.body._data_html_text

        if resume:
            return resume

        raise Exception(f'[ERROR] :: {resume=}')

    def has_doc_attachment(self, thread: Thread):
        """check if a resume has been sent before"""
        messages = thread._clean_thread
        sent = [x for x in messages if self._labels.sent in x.labelIds]

        if not sent:
            return False

        for message in sent:
            attachments = message._attachments
            for attachment in attachments:
                if attachment.mimeType == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                    return True

        return False

    def is_auto_reply(self, thread: Thread) -> bool:
        for message in thread.messages:
            if self._labels.auto_reply_enabled in message.labelIds:
                return True
        return False

    def is_debug(self, thread: Thread) -> bool:
        for message in thread.messages:
            if self._labels.debug in message.labelIds:
                return True
        return False

    def is_draft(self, message: Message) -> bool:
        if self._labels.draft in message.labelIds:
            return True
        return False

    def is_resume(self, thread: Thread):
        if self._labels.resume in thread._messages_labels:
            return True
        return False

    def is_sent(self, thread: Thread):
        if thread._clean_thread_latest is not None:
            if self._labels.sent in thread._clean_thread_latest.labelIds:
                return True
        return False

    def is_follow_up(self, thread: Thread):
        if self._labels.auto_reply_enabled in thread._messages_labels:
            if self._labels.sent in thread._messages_labels:
                if thread._message_first._email_from == thread._clean_thread_latest._email_from:
                    return True
        return False

    def is_waiting(self, thread: Thread):
        if thread._clean_thread_latest is not None:
            if self._labels.waiting in thread._clean_thread_latest.labelIds:
                return True
        return False

    def is_scheduled(self, thread: Thread):
        if self._labels.scheduled in thread._messages_labels:
            return True
        return False

    def is_analyze(self, thread: Thread):
        if self._labels.analyze in thread._messages_labels:
            return True
        return False

    def is_error(self, thread: Thread):
        if self._labels.error in thread._messages_labels:
            return True
        return False

    def is_skipped(self, thread: Thread):
        if self._labels.skipped in thread._messages_labels:
            return True
        return False

    def is_new(self, thread: Thread):
        if thread._clean_thread_latest:
            if self._labels.sent not in thread._clean_thread_latest.labelIds:
                return True
        return False

    def is_old(self, thread: Thread):
        if thread._clean_thread_latest:
            if thread._clean_thread_latest._date_since_now.days >= 3:
                return True
        return False

    def mark_processing(self, thread: Thread):
        return self.thread_modify(
            id=thread.id,
            addLabelIds=[self._labels.processing]
        )

    def needs_followup(
            self,
            thread: Thread,
            days: int = 3
    ) -> bool:
        message = thread._clean_thread_latest

        if self._labels.sent in message.labelIds:

            latest_date = dateutil.parser.parse(message.payload.get_header('Date').value)
            now = datetime.datetime.now()
            time_delta = ((now + latest_date.utcoffset()).replace(
                tzinfo=datetime.timezone(latest_date.utcoffset())) - latest_date)

            if time_delta.days <= 0:
                time_delta_check = f'last sent {round(time_delta.seconds / 60 / 60)} hours ago'
            else:
                time_delta_check = f'last sent {time_delta.days} days ago'

            debug(f'[*] checking :: {time_delta_check} :: {thread}')

            if time_delta.days >= days:
                debug(f'[*] needs_followup :: FOLLOW UP :: {thread}')
                return True

        return False

    def not_draft_and_trash(self, message: Message) -> bool:
        if (self._labels.draft not in message.labelIds and
                self._labels.trash not in message.labelIds):
            return True
        return False

    def unmark_processing(self, thread: Thread):
        return self.thread_modify(
            id=thread.id,
            removeLabelIds=[self._labels.processing]
        )
