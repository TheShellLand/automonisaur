""" It's always learning, growing. Forever and forever

Written         : Eric Jaw
Version         : 1.0
Created         : 2017-05-27

"""

from threading import Thread
from queue import Queue
import asyncio


def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


def stop_loop(loop):
    # Canceling pending tasks and stopping the loop
    asyncio.gather(*asyncio.Task.all_tasks()).cancel()

    # Stopping the loop
    loop.stop()

    # Received Ctrl+C
    return loop.close()


def create_queue():
    """ A large thread-safe stack of items nad have multiple threading pick items for processing

    :return: Instantiate the Queue object
    """

    return Queue()


def job(queue_object):
    """ This job is to run

    :return:
    """

    # TODO: Finish building out queue for jobs

    while not queue_object().not_empty():
        # Assign variables
        # Assign job
        try:
            pass
        except:
            pass
        pass

    return


def thread_spawn(target=None, thread_count=1):
    """ Create the number of threading specified by "thread_count" and target

    :param target: The target function for the threading to spawn from
    :param thread_count: The default number of threading to spawn
    :return:
    """

    if target is None:
        return Exception('No target specified for thread spawning')
    else:
        for thread in range(thread_count):
            t = Thread(target=target)
            return t.start()


def plumbing():
    worker_loop = asyncio.new_event_loop()  # Get a reference to the event loop
    worker = Thread(target=start_loop, args=(worker_loop,))
    worker.start()
