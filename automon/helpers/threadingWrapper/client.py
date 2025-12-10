import queue
import threading
import time

import automon

log = automon.helpers.loggingWrapper.logging.getLogger(__name__)
log.setLevel(automon.helpers.loggingWrapper.DEBUG)


class Thread(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
        super().__init__(group, target, name, args, kwargs)
        # Store arguments as public attributes
        self.public_target = target
        self.public_args = args
        self.public_kwargs = kwargs

        log.debug(f"[Thread] :: {target=} :: {args=} :: {kwargs=}")


class ThreadingClient(object):
    _global_threads_max: int = 1
    _global_threads_max_lock: threading.Lock = threading.Lock()

    def __init__(self):
        self.worker_queue: queue.Queue = queue.Queue()
        self.completed_queue: queue.Queue = queue.Queue()
        self.error_queue: queue.Queue = queue.Queue()

        self.threads_list: list[Thread] = []

        self.exit_event = threading.Event()

    def _thread_wrapper(self, target, args):
        current_thread = threading.current_thread()

        try:
            log.debug(f"[ThreadingClient] :: wrapper :: {current_thread.name} :: {target=} :: {args=}")
            result = target(*args)
            current_thread.result = result
            current_thread.exception = None
            self.completed_queue.put(current_thread)
        except Exception as error:
            log.error(f"[ThreadingClient] :: ERROR :: {error=}")
            current_thread.result = None
            current_thread.exception = error
            self.error_queue.put(current_thread)
            raise Exception(f"[ThreadingClient] :: ERROR :: {error=}")

    def add_worker(self, target: object, args: tuple):
        assert type(args) is tuple

        self.worker_queue.put((target, args))
        log.debug(f'[ThreadingClient] :: add_worker :: {target=} :: {args=}')
        return self

    def decrease_global_threads_max(self):
        """drops to 25%"""
        with ThreadingClient._global_threads_max_lock:
            old_value = ThreadingClient._global_threads_max
            new_value = int(ThreadingClient._global_threads_max * 0.25)

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
        return self.worker_queue.qsize() == 0 and all_threads_terminated

    def results(self):
        while self.completed_queue.qsize() > 0:
            result = self.completed_queue.get()
            if result.exception:
                log.warning(f"[ThreadingClient] :: ERROR :: {result.exception=}")
            log.debug(f'[ThreadingClient] :: results :: {result}')
            yield result

    def start(self, max_threads: int = None):

        if max_threads:
            with ThreadingClient._global_threads_max_lock:
                ThreadingClient._global_threads_max = max_threads

        while not self.is_done():

            self.threads_list = [t for t in self.threads_list if t.is_alive()]
            current_threads_count = len(self.threads_list)

            with ThreadingClient._global_threads_max_lock:
                max_threads_limit = ThreadingClient._global_threads_max

            if self.worker_queue.qsize() > 0 and current_threads_count < max_threads_limit:

                function, args = self.worker_queue.get()

                # thread = Thread(target=function, args=args)
                thread = Thread(target=self._thread_wrapper,
                                args=(function, args))

                self.threads_list.append(thread)

                thread.start()
                log.debug(f'[ThreadingClient] :: start :: {thread.name} :: running: '
                          f'{current_threads_count + 1} threads ({max_threads_limit} max)')

            else:
                time.sleep(0.1)

            if self.exit_event.is_set():
                break

        for thread in self.threads_list:
            thread.join()

        log.debug(f'[ThreadingClient] :: start :: {self._completed_threads_count} threads completed')
        return self

    @property
    def _current_threads_count(self):
        return len(self.threads_list)

    @property
    def _completed_threads_count(self):
        return self.completed_queue.qsize()

    def stop(self):
        self.exit_event.set()
        return self
