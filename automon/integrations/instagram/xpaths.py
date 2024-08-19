class XPaths(object):

    def __repr__(self):
        return 'Instagram XPaths'

    @property
    def authenticated_paths(self):
        authenticated = []
        authenticated.extend(self.profile_picture)
        authenticated.extend(self.home)
        return authenticated

    @property
    def home(self):
        return [
            '/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[1]/div/div/div/div/div[2]/div[1]/div/div/a/div',
        ]
