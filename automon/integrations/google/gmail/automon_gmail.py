import datetime
import dateutil.parser

from automon.helpers.debug import *

from .client import *


class AutomonLabels(GmailLabels):
    labels = {
        'automon': 'automon',
        "auto_reply_enabled": 'automon/auto reply enabled',
        'analyze': 'automon/analyze',
        'chat': 'automon/chat',
        'debug': 'automon/debug',
        'error': 'automon/error',
        "help": 'automon/help',
        "processing": 'automon/processing >>>',
        'resume': 'automon/resume',
        'relevant': 'automon/relevant',
        "remote": 'automon/remote',
        "user_action_required": 'automon/user action required',
        "waiting": 'automon/waiting',
        "welcome": 'automon/welcome',
    }

    def __init__(self):
        super().__init__()

        self.reset_labels = False

        # colors
        self._color_default = Color(backgroundColor='#653e9b', textColor='#e4d7f5')
        self._color_resume = Color(backgroundColor='#b65775', textColor='#ffffff')
        self._color_error = Color(backgroundColor='#cc3a21', textColor='#ffd6a2')
        self._color_enabled = Color(backgroundColor='#076239', textColor='#b9e4d0')
        self._color_welcome = Color(backgroundColor='#8e63ce', textColor='#ffffff')
        self._color_waiting = Color(backgroundColor='#cc3a21', textColor='#ffd6a2')
        self._color_processing = Color(backgroundColor='#cf8933', textColor='#ffd6a2')

        # required
        self.automon = Label(name=self.labels.get('automon'), color=self._color_default)

        # welcome
        self.welcome = Label(name=self.labels.get('welcome'), color=self._color_welcome)
        self.help = Label(name=self.labels.get('help'), color=self._color_welcome)

        # resume
        self.resume = Label(name=self.labels.get('resume'), color=self._color_resume)

        # analyze
        self.analyze = Label(name=self.labels.get('analyze'), color=self._color_default)

        # waiting
        self.waiting = Label(name=self.labels.get('waiting'), color=self._color_default)

        # currently processing
        self.processing = Label(name=self.labels.get('processing'), color=self._color_processing)

        # general
        self.draft = Label(name='DRAFT', id='DRAFT')
        self.sent = Label(name='SENT', id='SENT')
        self.unread = Label(name='UNREAD', id='UNREAD')
        self.trash = Label(name='TRASH', id='TRASH')

        # allow auto reply
        self.auto_reply_enabled = Label(name=self.labels.get('auto_reply_enabled'), color=self._color_enabled)

        # relevance
        self.relevant = Label(name=self.labels.get('relevant'), color=self._color_default)

        # remote
        self.remote = Label(name=self.labels.get('remote'), color=self._color_default)

        # need user input
        self.user_action_required = Label(name=self.labels.get('user_action_required'), color=self._color_error)

        # debugging
        self.debug = Label(name=self.labels.get('debug'), color=self._color_error)

        # error
        self.error = Label(name=self.labels.get('error'), color=self._color_error)

        # chat
        self.chat = Label(name=self.labels.get('chat'), color=self._color_error)

    @property
    def all_labels(self):
        return [
            getattr(self, x) for x in self.labels.keys()
            if not x.startswith("_")
            if not x == 'automon'
        ]


class AutomonGmailClient(GoogleGmailClient):
    labels = AutomonLabels()

    def __init__(self, config: GoogleGmailConfig = None):
        super().__init__(config)

    def create_labels(self):
        # create labels
        labels = self.labels
        labels.reset_labels = True

        for key, label in labels.labels.items():
            _get_label = getattr(labels, key)

            _id = _get_label.id
            _name = _get_label.name
            _color = _get_label.color

            if _get_label.id is None:
                _labels_get_by_name = self.labels_get_by_name(_name)

                if _labels_get_by_name.id is None:
                    _get_label._update_dict(
                        self.labels_create(
                            name=_name,
                            color=_color,
                        )
                    )
                else:
                    if labels.reset_labels:
                        self.labels_update(id=_labels_get_by_name.id, color=_color)

                    _get_label._update_dict(
                        _labels_get_by_name
                    )

    def clean_drafts(self, thread: Thread):
        for message in thread.messages:
            self.delete_draft(message)

    def delete_draft(self, message: Message):
        # delete DRAFT
        if self.labels.draft in message.automon_labels:
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
            labelIds=[self.labels.resume]
        )

        resume_selected = resume_search.messages[0]

        if resume_selected:
            return resume_selected

        resume_error = self.draft_create(
            draft_subject='resume missing',
            draft_to=self._userId,
            draft_body=f'Please copy and paste your resume here, and also add it as an attachment.',
        )

        self.messages_modify(
            id=resume_error.id,
            addLabelIds=[self.labels.automon, self.labels.error, self.labels.resume]
        )
        raise Exception(f'[ERROR] :: {resume_error}')

    def get_resume_text(self):

        resume_selected = self.get_resume_message()

        resume_attachments = next(resume_selected.automon_parts.automon_attachments())
        resume = resume_attachments.automon_parts[0].body.automon_data_html_text

        if resume:
            return resume

        raise Exception(f'[ERROR] :: {resume=}')

    def is_analyze(self, thread: Thread) -> bool:
        for message in thread.messages:
            if self.labels.analyze in message.automon_labels:
                return True
        return False

    def is_auto_reply(self, thread: Thread) -> bool:
        for message in thread.messages:
            if self.labels.auto_reply_enabled in message.automon_labels:
                return True
        return False

    def is_chat(self, thread: Thread) -> bool:
        for message in thread.messages:
            if self.labels.chat in message.automon_labels:
                return True
        return False

    def is_debug(self, thread: Thread) -> bool:
        for message in thread.messages:
            if self.labels.debug in message.automon_labels:
                return True
        return False

    def is_draft(self, message: Message) -> bool:
        if self.labels.draft in message.automon_labels:
            return True
        return False

    def is_resume(self, thread: Thread) -> bool:
        for message in thread.messages:
            if self.labels.resume in message.automon_labels:
                return True
        return False

    def is_sent(self, message: Message) -> bool:
        if self.labels.sent in message.automon_labels:
            return True
        return False

    def mark_processing(self, thread: Thread):
        return self.thread_modify(
            id=thread.id,
            addLabelIds=[self.labels.processing]
        )

    def needs_followup(
            self,
            thread: Thread,
            days: int = 3
    ) -> bool:
        message = thread.automon_clean_thread_latest

        if self.labels.sent in message.automon_labels:

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
        if (self.labels.draft not in message.automon_labels and
                self.labels.trash not in message.automon_labels):
            return True
        return False

    def unmark_processing(self, thread: Thread):
        return self.thread_modify(
            id=thread.id,
            removeLabelIds=[self.labels.processing]
        )
