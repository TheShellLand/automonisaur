class Format:
    blockquote = '>'
    codeblock = '```'


class Chat:
    @staticmethod
    def Format(msg: str, msg_format: Format):
        return f'{msg_format}{msg}'

    @staticmethod
    def wrap(msg: str, msg_format: Format):
        return f'{msg_format}{msg}{msg_format}'

    @staticmethod
    def none():
        return ''

    @staticmethod
    def clean(msg: str or None) -> str or None:
        if msg is None:
            return None
        return f'{msg}'.strip()

    @staticmethod
    def string(msg: str or None) -> str or None:
        if msg is None:
            return ''
        return f'{msg}'

    @staticmethod
    def multi_to_single_line(msg: str) -> str:
        if msg is None:
            return f''

        if '\n' in msg and msg is not None:

            new_msg = []
            split = msg.splitlines()

            for line in split:
                if line:
                    line = line.strip()
                    line = Chat.clean(line)
                    new_msg.append(line)

            new_msg = ' '.join(new_msg)

            return new_msg

        return msg
