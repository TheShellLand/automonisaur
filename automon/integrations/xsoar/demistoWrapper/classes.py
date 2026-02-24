class Dict:

    def __init__(self):
        pass

    def __eq__(self, other):
        if self.__dict__ == other.__dict__:
            return True
        return False

    def _flatten(self) -> dict:
        flatten = {}

        for key, value in self.__dict__.items():

            if key == 'CustomFields':
                continue

            if type(value) == dict:
                flatten.update(self._flatten_dict(value))
            elif type(value) == list:
                flatten.update(self._flatten_list(key, value))
            else:
                flatten[key] = value

        return flatten

    def _flatten_dict(self, value: dict) -> dict:
        flatten = {}

        if type(value) == dict:
            for item in value.items():
                key, value = item

                if type(value) == list:
                    flatten.update(self._flatten_list(key, value))

                elif type(value) == dict:
                    flatten.update(self._flatten_dict(value))

                else:
                    flatten[key] = value

        return flatten

    def _flatten_list(self, key: str, value: list) -> dict:

        flatten = {}

        if type(value) == list:
            for value_ in value:
                if type(value_) == dict:
                    flatten.update(self._flatten_dict(value_))
                elif type(value_) == list:
                    flatten.update(self._flatten_list(key, value_))
                else:
                    flatten[key] = value

        return flatten

    def _update(self, update: dict | str | object):

        if isinstance(update, str):
            return self._update_json(update)

        if hasattr(update, '__dict__'):
            update = update.__dict__

        return self._update_dict(update)

    def _update_dict(self, update: dict):
        self.__dict__.update(update)
        return self

    def _update_json(self, update: str):
        import json
        update = json.loads(update)
        return self._update_dict(update)

    def update(self, update: dict | str):
        return self._update(update)

    def to_dict(self):
        if self.to_json():
            return self.__dict__
        raise Exception(f"[DictUpdate] :: ERROR :: can't serialized :: {self.__dict__}")

    def _to_json(self, indent: int = None):
        import json
        try:
            return json.dumps(self.__dict__, indent=indent)
        except Exception as error:
            raise Exception(f'ERROR :: {error=} :: {self.__dict__}')

    def to_json(self, indent: int = None):
        return self._to_json(indent)


class DictUpdate:

    def __init__(self):
        pass

    def __eq__(self, other):
        if self.__dict__ == other.__dict__:
            return True
        return False

    def _update(self, dict_: dict):
        if hasattr(dict_, '__dict__'):
            dict_ = dict_.__dict__
        self.__dict__.update(dict_)
        return self

    def update(self, dict_: dict):
        return self._update(dict_)

    def to_dict(self):
        if self.to_json():
            return self.__dict__
        raise Exception(f"[DictUpdate] :: ERROR :: can't serialized :: {self.__dict__}")

    def _to_json(self, indent: int = None):
        import json
        try:
            return json.dumps(self.__dict__, indent=indent)
        except Exception as error:
            raise Exception(f'ERROR :: {error=} :: {self.__dict__}')

    def to_json(self, indent: int = None):
        return self._to_json(indent)


class Demisto(DictUpdate):
    pass


class DemistoContext(DictUpdate):

    def __init__(self, context: dict = None):
        super().__init__()

        if context:
            self.update(context)
