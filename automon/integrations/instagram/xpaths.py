class XPaths(object):

    def __repr__(self):
        return 'Instagram XPaths'

    @property
    def login_user(self):
        return [
            '/html/body/div[2]/div/div/div[1]/div/div/div/div[1]/section/main/div/div/div[1]/div[2]/form/div/div[1]/div/label/input',
            '/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/section/main/div/div/div[1]/div[2]/form/div/div[1]/div/label/input',
        ]

    @property
    def login_pass(self):
        return [
            '/html/body/div[2]/div/div/div[1]/div/div/div/div[1]/section/main/div/div/div[1]/div[2]/form/div/div[2]/div/label/input',
            '/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/section/main/div/div/div[1]/div[2]/form/div/div[2]/div/label/input'
        ]

    @property
    def login_btn(self):
        return [
            '/html/body/div[2]/div/div/div[1]/div/div/div/div[1]/section/main/div/div/div[1]/div[2]/form/div/div[3]/button',
            '/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/section/main/div/div/div[1]/div[2]/form/div/div[3]/button'
        ]

    @property
    def profile_picture(self):
        return [
            '/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/section/main/div[1]/section/div[3]/div[1]/div/div/div/div/div/div[1]/div/div/span/img',
            '/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/section/main/div[1]/section/div/div[2]/div/div/div/div/ul/li[3]/div/button/div[1]/span/img',
        ]

    @property
    def save_info(self):
        return '/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/section/main/div/div/div/section/div/button'

    @property
    def save_info_not_now(self):
        return ['/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/section/main/div/div/div/div',
                '/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/section/main/div/div/div/div/button']

    @property
    def turn_on_notifications(self):
        return [
            '/html/body/div[2]/div/div/div[3]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/button[1]',
            '/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/button[1]'
        ]

    @property
    def turn_on_notifications_not_now(self):
        return [
            '/html/body/div[2]/div/div/div[3]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/button[2]',
            '/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/button[2]'
        ]
