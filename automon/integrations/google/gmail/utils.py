from automon import debug

from .classes import *

labels = AutomonLabels()


def is_resume(thread: Thread):
    if labels.resume in thread._messages_labels:
        return True
    return False


def has_doc_attachment(thread: Thread):
    """check if a resume has been sent before"""
    messages = thread._clean_thread
    sent = [x for x in messages if labels.sent in x.labelIds]

    if not sent:
        return False

    for message in sent:
        attachments = message._attachments
        for attachment in attachments:
            if attachment.mimeType == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                return True

    return False


def is_skipped(thread: Thread):
    if labels.skipped in thread._messages_labels:
        return True
    return False


def is_error(thread: Thread):
    if labels.error in thread._messages_labels:
        return True
    return False


def is_analyze(thread: Thread):
    if labels.analyze in thread._messages_labels:
        return True
    return False


def is_scheduled(thread: Thread):
    if labels.scheduled in thread._messages_labels:
        return True
    return False


def is_sent(thread: Thread):
    if thread._clean_thread_latest is not None:
        if labels.sent in thread._clean_thread_latest.labelIds:
            return True
    return False


def is_old(thread: Thread):
    if thread._clean_thread_latest:
        if thread._clean_thread_latest._date_since_now.days >= 3:
            return True
    return False


def is_new(thread: Thread):
    if thread._clean_thread_latest:
        if labels.sent not in thread._clean_thread_latest.labelIds:
            return True
    return False


def is_follow_up(thread: Thread):
    if labels.auto_reply_enabled in thread._messages_labels:
        if labels.sent in thread._messages_labels:
            if thread._message_first._email_from == thread._clean_thread_latest._email_from:
                return True
    return False
