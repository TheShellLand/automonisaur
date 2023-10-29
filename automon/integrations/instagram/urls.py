class Urls(object):

    def __repr__(self):
        return f'Instagram URLs'

    @property
    def domain(self):
        return 'https://www.instagram.com'

    @property
    def login_page(self):
        return f'{self.domain}/accounts/login/?source=auth_switcher'

    def followers(self, account: str):
        return f'{self.domain}/{account}/followers/'

    def following(self, account: str):
        return f'{self.domain}/{account}/following/'
