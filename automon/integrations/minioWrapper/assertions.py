from automon.helpers.loggingWrapper import LoggingClient, DEBUG, INFO

logger = LoggingClient.logging.getLogger(__name__)
logger.setLevel(DEBUG)


class MinioAssertions:

    @staticmethod
    def bucket_name(bucket: str) -> bool:
        if bucket == f'{bucket}'.lower():
            return f'{bucket}'
        logger.warning(msg=f'bucket name "{bucket}" must be lower')
        return f'{bucket}'.lower()
