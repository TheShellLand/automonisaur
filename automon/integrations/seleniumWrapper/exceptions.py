class ActionClickException(Exception):
    pass


class ActionTypeException(Exception):
    pass


class ElementNotFoundException(Exception):
    pass


class XpathNotFoundException(ElementNotFoundException):
    pass
