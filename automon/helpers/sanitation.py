from string import (ascii_letters, digits)


class Sanitation:

    @staticmethod
    def strip_quotes(text):
        removed_chars = ['"', "'"]

        text = str(text)

        for char in removed_chars:
            text = text.strip(char)

        return text

    @staticmethod
    def strip_spaces(text: str) -> str:
        removed_chars = ' '

        text = str(text)
        text = text.strip(removed_chars)

        return text

    @staticmethod
    def strip_spaces_from_list(lst: list) -> list:
        removed_chars = ' '

        new_list = list()

        for item in lst:
            item = str(item)
            item = item.strip(removed_chars)
            new_list.append(item)

        return new_list

    @staticmethod
    def safe_string(text):
        allowed_characters = ascii_letters + digits + '-_.'

        text = str(text)
        new_text = []

        for character in text:
            if character in allowed_characters:
                new_text.append(character)
            else:
                new_text.append('_')

        return ''.join(new_text)

    @staticmethod
    def dedup(object):
        """
        deduplicate object
        """
        new_list = []
        for item in object:
            if item not in new_list:
                new_list.append(item)

        return new_list

    @staticmethod
    def list_from_string(string: str) -> list:
        if not string:
            return list()

        new_lst = list()

        if ',' in string:
            new_lst = string.split(',')
        elif ' ' in string:
            new_lst = string.split(' ')
        else:
            string = Sanitation.strip_quotes(string)
            string = Sanitation.strip_spaces(string)
            new_lst.append(string)
            return new_lst

        # TODO: clean list before returning it

        for item in new_lst:
            item = Sanitation.strip_quotes(item)
            item = Sanitation.strip_spaces(item)
            new_lst.append(item)

        return Sanitation.strip_spaces_from_list(new_lst)
