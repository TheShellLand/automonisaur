from .tokens import Tokens


class Identity:
    def __init__(self, content: str = '', role: str = 'system'):
        self.role: str = role
        self.content: str = content

    def __repr__(self):
        return f'{self.role} :: {self.content} :: {len(Tokens(self.content))} tokens'

    def __bool__(self):
        return bool(self.role and self.content)

    def __eq__(self, other):
        return (self.role, self.content) == (other.role, other.content)

    def to_dict(self):
        return {'role': self.role, 'content': self.content}


class HumanAgent(Identity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class RecruiterAgent(Identity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
