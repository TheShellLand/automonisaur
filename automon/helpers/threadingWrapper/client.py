import queue
import threading
import time

import automon

log = automon.helpers.loggingWrapper.logging.getLogger(__name__)
log.setLevel(automon.helpers.loggingWrapper.DEBUG)


class ThreadingClient(object):
    global_threads_max: int = 1
    global_threads: list = []

    def __init__(self):
        self.worker_queue: queue.Queue = queue.Queue()
        self.completed_queue: queue.Queue = queue.Queue()

        self.exit_event = threading.Event()

    def add_worker(self, target: object, args: tuple):
        assert type(args) is tuple

        self.worker_queue.put((target, args))
        log.debug(f'[ThreadingClient] :: add_worker :: {target=} -> {args=}')
        return self

    def increase_global_threads_max(self):
        """doubles every worker completed"""
        old_value = self.global_threads_max
        new_value = int(self.global_threads_max * 2)

        self.global_threads_max = new_value

        log.debug(f'[ThreadingClient] :: global_threads_max :: {old_value} -> {new_value}')
        return self

    def decrease_global_threads_max(self):
        """drops to 25%"""
        old_value = self.global_threads_max
        new_value = int(self.global_threads_max * 0.25)

        self.global_threads_max = new_value

        log.debug(f'[ThreadingClient] :: global_threads_max :: {old_value} -> {new_value}')
        return self

    def start(self):

        while self.worker_queue.qsize() > 0 or any(t.is_alive() for t in self.global_threads):

            self.global_threads = [t for t in self.global_threads if t.is_alive()]
            current_running_threads = len(self.global_threads)

            if self.worker_queue.qsize() > 0 and current_running_threads < self.global_threads_max:
                function, args = self.worker_queue.get()
                thread = threading.Thread(target=function, args=tuple(args))
                thread.start()
                self.global_threads.append(thread)
                log.debug(f'[ThreadingClient] :: start :: running: '
                          f'{len(self.global_threads)}/{self.global_threads_max}')

            else:
                time.sleep(0.1)

            if self.exit_event.is_set():
                break

        for thread in self.global_threads:
            thread.join()
            self.completed_queue.put(thread)

        log.debug(f'[ThreadingClient] :: start :: {self.completed_queue.qsize()} threads completed')
        return self

    def results(self):
        while self.completed_queue.qsize() > 0:
            result = self.completed_queue.get()
            log.debug(f'[ThreadingClient] :: results :: {result}')
            yield result

    def is_done(self):
        """Non-blocking check to see if all threads are done."""
        # Returns True if ALL threads are not alive (i.e., finished)
        return all(not t.is_alive() for t in self.running_threads)

    def stop(self):
        self.exit_event.set()
        return self

    @property
    def total_global_threads(self):
        return len(self.global_threads)
