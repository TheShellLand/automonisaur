class Urls(object):

    def __repr__(self):
        return f'Instagram URLs'

    @property
    def login_page(self):
        return 'https://www.instagram.com/accounts/login/?source=auth_switcher'

    @staticmethod
    def followers(account: str):
        return f'https://www.instagram.com/{account}/followers/'

    @staticmethod
    def following(account: str):
        return f'https://www.instagram.com/{account}/following/'
