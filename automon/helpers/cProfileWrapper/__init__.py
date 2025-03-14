import cProfile


class CProfile:
    """
    pr = cProfile.Profile()
    pr.enable()

    chat.print_stream()

    pr.disable()
    pr.print_stats(sort='cumulative')
    """

    def __init__(self, func, *args, **kwargs):

        pr = cProfile.Profile()
        pr.enable()

        try:
            func(*args, **kwargs)
        except Exception as error:
            pr.disable()
            pr.print_stats(sort='cumulative')
            pr.print_stats(sort='ncalls')
            raise Exception(error)

        pr.disable()
        pr.print_stats(sort='cumulative')
