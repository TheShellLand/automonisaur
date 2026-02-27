from automon import debug

from .classes import *

labels = AutomonLabels()


def is_resume(thread: Thread):
    if labels.resume in thread.automon_messages_labels:
        debug('resume')
        return True
    return False


def has_doc_attachment(thread: Thread):
    """check if a resume has been sent before"""
    messages = thread.automon_clean_thread
    sent = [x for x in messages if labels.sent in x.automon_labels]

    if not sent:
        return False

    for message in sent:
        attachments = message.automon_attachments
        for attachment in attachments:
            if attachment.mimeType == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                return True

    return False


def is_skipped(thread: Thread):
    if labels.skipped in thread.automon_messages_labels:
        debug('skipped')
        return True
    return False


def is_error(thread: Thread):
    if labels.error in thread.automon_messages_labels:
        debug('error')
        return True
    return False


def is_chat(thread: Thread):
    if labels.chat in thread.automon_messages_labels:
        debug('chat')
        return True
    return False


def is_analyze(thread: Thread):
    if labels.analyze in thread.automon_messages_labels:
        debug('analyze')
        return True
    return False


def is_scheduled(thread: Thread):
    if labels.scheduled in thread.automon_messages_labels:
        debug('scheduled')
        return True
    return False


def is_sent(thread: Thread):
    if labels.sent in thread.automon_clean_thread_latest.automon_labels:
        return True
    return False


def is_old(thread: Thread):
    if thread.automon_clean_thread_latest.automon_date_since_now.days >= 3:
        debug('followup')
        return True
    return False


def is_new(thread: Thread):
    if labels.sent not in thread.automon_clean_thread_latest.automon_labels:
        debug('new')
        return True
    return False


def is_follow_up(thread: Thread):
    if labels.auto_reply_enabled in thread.automon_messages_labels:
        if labels.sent in thread.automon_messages_labels:
            if thread.automon_message_first.automon_email_from == thread.automon_clean_thread_latest.automon_email_from:
                return True
    return False
