from concurrent.futures import (ThreadPoolExecutor, wait, as_completed)


class ThreadPool:

    @staticmethod
    def config_thread_pool(thread_pool: int = 1) -> ThreadPoolExecutor:
        """Configure threading pool

        thread_pool: must be > 0
        """
        if not thread_pool:
            thread_pool = 1
        return ThreadPoolExecutor(max_workers=thread_pool)
