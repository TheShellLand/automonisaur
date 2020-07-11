from string import (ascii_letters, digits)


class Sanitation:

    @staticmethod
    def no_quotes(text):
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

        new = list()

        for item in lst:
            item = str(item)
            item = item.strip(removed_chars)
            new.append(item)

        return new

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
