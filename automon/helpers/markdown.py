import textwrap


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


class Markdown:

    @staticmethod
    def list_to_markdown(markdowns: list[str]) -> str:
        return Markdown.lstrip(
            '\n\n---\n\n'.join(markdowns)
        )

    @staticmethod
    def lstrip(text: str) -> str:
        if text is None:
            return

        return textwrap.dedent(
            '\n'.join(line.lstrip() for line in text.strip().splitlines())
        ).strip()

    @staticmethod
    def str_to_markdown(
            header: str,
            text: str,
            header_level: int = 1,
    ) -> str:
        header_weight = '#' * header_level

        raw_template = f"""
        {header_weight} {header.upper()}

        ```text
        {text}
        ```
        """

        return Markdown.lstrip(raw_template)
