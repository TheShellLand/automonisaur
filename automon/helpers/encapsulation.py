def encapsulate(value, object_class):
    if isinstance(value, list):
        return [x if isinstance(x, object_class) else object_class(x) for x in value]

    if isinstance(value, object_class):
        return value

    if value is not None:
        return object_class(value)

    return value
