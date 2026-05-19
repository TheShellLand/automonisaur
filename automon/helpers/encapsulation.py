def encapsulate(value, object_class):
    if isinstance(value, list):
        new_list = []
        for item in value:
            if isinstance(item, object_class):
                new_list.append(item)
                continue

            if isinstance(item, dict):
                new_list.append(object_class(item))
                continue

            new_list.append(item)

        return new_list

    if isinstance(value, object_class):
        return value

    if isinstance(value, dict):
        return object_class(value)

    return value
