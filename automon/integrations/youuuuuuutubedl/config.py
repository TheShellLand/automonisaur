import os

from automon.integrations.requestsWrapper import RequestsClient


class YoutubeConfig(object):

    def __init__(self):
        pass

    def isReady(self):
        return

    def download_youtubedl(self):
        """Download binary
        """
        url = 'https://github.com/ytdl-org/youtube-dl/releases/download/2021.12.17/youtube-dl'
        return RequestsClient(url=url)
