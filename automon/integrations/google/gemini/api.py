class GoogleGeminiApi(object):

    def __init__(self):
        self.url: str = ''

    @property
    def base(self):
        self.url = 'https://generativelanguage.googleapis.com'
        return self

    @property
    def v1beta(self):
        self.url += f'/v1beta'
        return self

    @property
    def models(self):
        self.url += f'/models'
        return self

    @property
    def gemini(self):
        self.url += f'/gemini-1.5-flash'
        return self

    @property
    def generateContent(self):
        self.url += f':generateContent'
        return self

    def key(self, key: str):
        self.url += f'?key={key}'
        return self
