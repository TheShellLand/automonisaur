from string import (ascii_letters, digits)


class Sanitation:

    @staticmethod
    def hyphen_underscore(text: str) -> str:
        allowed_chars = [x for x in ''.join([ascii_letters, digits, '-', '_'])]

        text = f'{text}'

        return ''.join([x for x in text if x in allowed_chars])

    @staticmethod
    def hyphens_only(text: str) -> str:
        allowed_chars = [x for x in ''.join([ascii_letters, digits, '-'])]

        text = f'{text}'

        return ''.join([x for x in text if x in allowed_chars])

    @staticmethod
    def underscores_only(text: str) -> str:
        allowed_chars = [x for x in ''.join([ascii_letters, digits, '_'])]

        text = f'{text}'

        return ''.join([x for x in text if x in allowed_chars])

    @staticmethod
    def strip_quotes(text: str) -> str:
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
    def strip(text: str) -> str:
        return str(text).strip()

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
    def ascii_numeric_only(text: str) -> str:
        allowed_characters = ascii_letters + digits

        text = str(text).strip()
        new_text = []

        for character in text:
            if character in allowed_characters:
                new_text.append(character)
            else:
                new_text.append('_')

        return ''.join(new_text)

    @staticmethod
    def safe_string(text: str) -> str:
        allowed_characters = ascii_letters + digits + '-_.'

        text = str(text).strip()
        new_text = []

        for character in text:
            if character in allowed_characters:
                new_text.append(character)
            else:
                new_text.append('_')

        return ''.join(new_text)

    @staticmethod
    def safe_string_allow_spaces(text: str) -> str:
        allowed_characters = ascii_letters + digits + '-_. '

        text = str(text).strip()
        new_text = []

        for character in text:
            if character in allowed_characters:
                new_text.append(character)
            else:
                new_text.append('_')

        return ''.join(new_text)

    @staticmethod
    def safe_filename(text: str) -> str:
        allowed_characters = ascii_letters + digits + '''-_.:?'" '''

        text = str(text).strip()
        new_text = []

        for character in text:
            if character in allowed_characters:
                new_text.append(character)
            else:
                new_text.append('_')

        return ''.join(new_text)

    @staticmethod
    def safe_foldername(text: str) -> str:
        allowed_characters = ascii_letters + digits + '''-_. '''

        text = str(text).strip()
        new_text = []

        for character in text:
            if character in allowed_characters:
                new_text.append(character)
            else:
                new_text.append('_')

        return ''.join(new_text)

    @staticmethod
    def dedup(lst: list) -> list:
        """deduplicate list"""

        new_list = []
        for item in lst:
            if item not in new_list:
                new_list.append(item)

        return new_list

    @staticmethod
    def list_from_string(string: str) -> list:
        if not string:
            return list()

        string = Sanitation.strip_spaces(string)

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

        new_lst = [Sanitation.strip_quotes(item) for item in new_lst]
        new_lst = [Sanitation.strip_spaces(item) for item in new_lst]

        return Sanitation.strip_spaces_from_list(new_lst)
