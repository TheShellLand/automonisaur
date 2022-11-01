from concurrent.futures import (ThreadPoolExecutor, wait, as_completed)


class ThreadPool:

    @staticmethod
    def config_thread_pool(thread_pool: int) -> ThreadPoolExecutor:
        """Configure threading pool
        """
        return ThreadPoolExecutor(max_workers=thread_pool)
