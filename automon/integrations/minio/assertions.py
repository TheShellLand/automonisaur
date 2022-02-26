from automon import Logging

log = Logging(name='MinioAssertions', level=Logging.DEBUG)


class MinioAssertions:

    @staticmethod
    def bucket_name(bucket: str) -> bool:
        if bucket == f'{bucket}'.lower():
            return bucket
        log.warn(msg=f'bucket name "{bucket}" must be lower')
        return f'{bucket}'.lower()
