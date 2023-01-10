class XPaths(object):

    def __repr__(self):
        return 'Instagram XPaths'

    @property
    def login_user(self):
        return '/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/section/main/div/div/div[1]/div[2]/form/div/div[1]/div/label/input'

    @property
    def login_pass(self):
        return '/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/section/main/div/div/div[1]/div[2]/form/div/div[2]/div/label/input'

    @property
    def login_btn(self):
        return '/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/section/main/div/div/div[1]/div[2]/form/div/div[3]/button'

    @property
    def profile_picture(self):
        return '/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/section/nav/div[2]/div/div/div[3]/div/div[6]'

    @property
    def save_info(self):
        return '/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/section/main/div/div/div/section/div/button'

    @property
    def save_info_not_now(self):
        return '/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/section/main/div/div/div/div/button'

    @property
    def turn_on_notifications(self):
        return '/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/button[1]'

    @property
    def turn_on_notifications_not_now(self):
        return '/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/button[2]'