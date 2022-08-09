class Urls(object):

    def __repr__(self):
        return f'Instagram URLs'

    @property
    def login_page(self):
        return 'https://www.instagram.com/accounts/login/?source=auth_switcher'
