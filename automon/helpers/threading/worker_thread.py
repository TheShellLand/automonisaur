import queue
import threading
import time

print_lock = threading.Lock()


def init_queue():
    """ Initialize the Queue """
    return queue.Queue()


def job(queue_item):
    """ What is actually being worked on """

    with print_lock:
        print('+ Job:', threading.current_thread().getName())

    args = dict()
    for key in queue_item:
        if key == 'headers':
            args['headers'] = queue_item[key]
            # Disabled Neo4j
            # http.http_header(**args)

    else:
        args = queue_item


def worker(queue_list):
    """ Worker puts the things to work """

    while True:

        queue_item = queue_list.get()

        if queue_item:
            with print_lock:
                print('+ Worker:', threading.current_thread().getName())

            # TODO: Find a way to figure out what data is before doing work on it
            # TODO: Add failure routine if queue_item is a str and not a list

            job(queue_item)

            queue_list.task_done()

        else:
            return


def start_worker(queue_list):
    """ This starts all the threading """

    print('+ Queue:', queue_list.qsize())

    try:
        num_worker_threads = 100 if queue_list.qsize() > 100 else queue_list.qsize()
        threads = []
        for _ in range(num_worker_threads):
            t = threading.Thread(target=worker, args=(queue_list,))
            t.setDaemon(True)
            t.start()
            threads.append(t)

        start = time.time()

        print('+ Threads started:', len(threads))
        for _ in threads:
            print('`-', _)

        # queue_list.join()  # block until all tasks are done

        print('+ Entire job took:', time.time() - start)

        print('+ Threads enumerate:', len(threading.enumerate()))
        for _ in threading.enumerate():
            print('`-', _)

        for _ in range(num_worker_threads):  # stop workers
            queue_list.put(None)
        # for _ in threading:
        #     _.join()

        # print(threading.current_thread().getName(), 'is', threading.Thread.is_alive(threading.current_thread()))

    except:
        raise
