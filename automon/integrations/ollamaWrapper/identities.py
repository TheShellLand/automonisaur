from .tokens import Tokens
from .prompt_templates import *


class Identity:
    def __init__(self, content: str = ''):
        self.role: str = AgentRole.SYSTEM
        self._content: str = content

    def __repr__(self):
        return f'{self.role} :: {self.content} :: {len(Tokens(self.content))} tokens'

    def __bool__(self):
        return bool(self.role and self.content)

    def __eq__(self, other):
        return (self.role, self.content) == (other.role, other.content)

    @property
    def content(self):
        return Markdown.lstrip(self._content)

    @content.setter
    def content(self, content: str):
        self._content = Markdown.lstrip(content)

    def add_memory(self, memory: str):
        self.content = Markdown.list_to_markdown([
            self.content,
            Markdown.lstrip(memory)
        ])
        return self

    def to_dict(self):
        return {'role': self.role, 'content': self.content}


class HumanAgent(Identity):
    def __init__(self, name: str, memory: str):
        super().__init__()
        self.content = AgentTemplates.your_identity(
            name=name,
            memory=Markdown.lstrip(memory),
        )


class RecruiterAgent(Identity):
    def __init__(self):
        super().__init__()
