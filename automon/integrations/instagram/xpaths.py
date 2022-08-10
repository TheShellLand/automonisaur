class XPaths(object):

    def __repr__(self):
        return 'Instagram XPaths'

    @property
    def login_user(self):
        return '//*[@id="loginForm"]/div/div[1]/div/label/input'

    @property
    def login_pass(self):
        return '//*[@id="loginForm"]/div/div[2]/div/label/input'

    @property
    def login_button(self):
        return '//*[@id="loginForm"]/div/div[3]/button'

    @property
    def login_pass_xpaths(self):
        return [
            '//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[3]/div/label/input',
            '//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[4]/div/label/input'
        ]

    @property
    def login_btn_xpaths(self):
        return [
            '//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[4]/button',
            '//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[6]/button'
        ]

    @property
    def save_your_login_info(self):
        return '//*[@id="react-root"]/section/main/div/div/div/section/div/button'