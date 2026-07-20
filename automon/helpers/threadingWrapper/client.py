import queue
import threading
import time

import automon

from automon.helpers import *

log = automon.helpers.loggingWrapper.logging.getLogger(__name__)
log.setLevel(automon.helpers.loggingWrapper.DEBUG)


class Thread(threading.Thread):
    def __init__(
            self,
            group=None,
            target=None,
            name=None,
            daemon=None,
            args=(),
            kwargs={}
    ):
        super().__init__(
            group=group,
            target=target,
            name=name,
            daemon=daemon,
            args=args,
            kwargs=kwargs,
        )
        # Store arguments as public attributes
        self._target = target
        self._target_args = args
        self._target_kwargs = kwargs

    def __repr__(self):
        return f'[Thread] :: {self.name} :: {self._target_args}'


class ThreadingClient(object):
    _global_threads_max: int = 1
    _global_threads_max_lock: threading.Lock = threading.Lock()

    def __init__(self):
        self.queue_worker: queue.Queue = queue.Queue()
        self.queue_completed: queue.Queue = queue.Queue()
        self.queue_error: queue.Queue = queue.Queue()

        self.threads_list: list[Thread] = []

        self.exit_event = threading.Event()

    def _thread_wrapper(self, target, args):
        current_thread = threading.current_thread()

        try:
            log.debug(f"[ThreadingClient] :: wrapper :: {current_thread.name} :: {target=} :: {args=}")
            if args is not None:
                result = target(*args)
            else:
                result = target()

            current_thread.result = result
            current_thread.exception = None
            self.queue_completed.put(current_thread)
        except Exception as error:
            current_thread.result = None
            current_thread.exception = error
            self.queue_error.put(current_thread)
            raise error

    def add_worker(
            self,
            target: object,
            args: tuple = None,
            raise_exception: bool = True
    ):
        if args is not None:
            assert type(args) is tuple

        self.queue_worker.put((target, args))
        log.debug(f'[ThreadingClient] :: add_worker :: {target=} :: {args=}')
        return self

    def decrease_global_threads_max(self):
        """drops to 25%"""
        with ThreadingClient._global_threads_max_lock:
            old_value = ThreadingClient._global_threads_max
            new_value = int(ThreadingClient._global_threads_max * 0.25)

            if new_value > 0:
                ThreadingClient._global_threads_max = new_value

        log.debug(f'[ThreadingClient] :: global_threads_max :: {old_value} -> {new_value}')
        return self

    def increase_global_threads_max(self):
        """doubles every worker completed"""
        with ThreadingClient._global_threads_max_lock:
            old_value = ThreadingClient._global_threads_max
            new_value = int(ThreadingClient._global_threads_max * 2)

            ThreadingClient._global_threads_max = new_value

        log.debug(f'[ThreadingClient] :: global_threads_max :: {old_value} -> {new_value}')
        return self

    def is_done(self):
        # Returns True if ALL threads are not alive (i.e., finished)
        self.threads_list = [t for t in self.threads_list if t.is_alive()]

        all_threads_terminated = all(not t.is_alive() for t in self.threads_list)

        # The client is 'done' only when BOTH conditions are met
        return self.queue_worker.qsize() == 0 and all_threads_terminated

    def results(self):
        # 1. Process all successfully completed threads first
        while self.queue_completed.qsize() > 0:
            result = self.queue_completed.get()
            log.debug(f'[ThreadingClient] :: results :: {result}')
            self.queue_completed.task_done()
            yield result

        # 2. Process and yield all failed threads so errors aren't swallowed
        while self.queue_error.qsize() > 0:
            result = self.queue_error.get()
            if result.exception:
                log.warning(f"[ThreadingClient] :: ERROR :: {result.exception=}")
            log.debug(f'[ThreadingClient] :: results (error) :: {result}')
            self.queue_error.task_done()
            yield result

    def start(self, max_threads: int = None):

        if max_threads is None:
            max_threads = self.queue_worker.qsize()

        with ThreadingClient._global_threads_max_lock:
            ThreadingClient._global_threads_max = max_threads

        while not self.is_done():

            self.threads_list = [t for t in self.threads_list if t.is_alive()]
            current_threads_count = len(self.threads_list)

            with ThreadingClient._global_threads_max_lock:
                max_threads_limit = ThreadingClient._global_threads_max

            if self.queue_worker.qsize() > 0 and current_threads_count < max_threads_limit:

                function, args = self.queue_worker.get()

                # thread = Thread(target=function, args=args)
                thread = Thread(
                    target=self._thread_wrapper,
                    args=(function, args),
                    name=getattr(function, '__name__')
                )

                self.threads_list.append(thread)

                thread.start()
                self.queue_worker.task_done()

                log.debug(repr_str([
                    f'[ThreadingClient] :: start',
                    f'running :: {thread.name}, '
                    f'{thread._target_args}',
                    f'{current_threads_count + 1} threads ({max_threads_limit} max)',
                ]))

            else:
                time.sleep(0.1)

            if self.exit_event.is_set():
                break

        for thread in self.threads_list:
            thread.join()

        return self

    @property
    def _current_threads_count(self):
        return len(self.threads_list)

    @property
    def _completed_threads_count(self):
        return self.queue_completed.qsize()

    def stop(self):
        self.exit_event.set()
        return self
