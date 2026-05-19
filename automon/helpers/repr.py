def repr_str(repr_list: list):
    repr_list = [str(x) for x in repr_list if x and x is not None]
    return ' :: '.join(repr_list)
