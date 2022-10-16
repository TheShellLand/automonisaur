import bcrypt
import random

from flask import (redirect, url_for, session, flash)
from flask import (session, redirect, url_for)
from flask_login import (logout_user, login_user, login_fresh,
                         current_user, LoginManager, UserMixin)

from .auth_creds import credential_db


def login_manager_wrapper(app):
    """ Wrapper for flask_login.LoginManager()

    :param app: Flask app name to initialize
    :return: flask_login.LoginManager object
    """

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.session_protection = "strong"

    # login_manager = app_userloader.login_init()
    # login_manager.login_view = 'login'

    return login_manager


def load_user(user_id):
    """ Callback to reload the user object

    :param user_id: User.id to look up
    :return: user UserMixin class
    """

    # user = User()
    user = UserMixin()
    user.id = user_id
    return user


def login(request):
    """ This authenticates the user login with the internal user database

    :return: True if authenticated; False, with error message
    """

    if request.method == 'POST':

        if 'username' in request.form:
            username = str(request.form['username']).strip().lower()

        if 'password' in request.form:
            password = request.form['password'].encode()

        if 'remember' in request.form:
            remember = True
        else:
            remember = False

        if 'force' in request.form:
            # Disable force flag
            # user_id will need to be active to proceed
            # force = True
            force = False
        else:
            force = False

        credentials = credential_db()

        errors = [
            '''Well, that didn't work''',
            '''Everything is wrong''',
            '''Did not work''',
            '''Hello?''',
            '''Why don't you try again?''',
            '''Try again''',
            '''Login: ixzd2@skynt Password: lost''',
            '''Password is password''',
            '''I'm sorry Dave, but I can't do that''',
            '''This is borderline harrassment''',
            '''Not cool''',
            '''If you're looking for something, you're doing it wrong''',
            '''Aren't you a persistent one?''',
            '''I'm sorry, what are you looking for?''',
            '''Find a hero in you''',
            '''This isn't getting anywhere''',
            '''Let's play a game''',
            ''':('''
        ]

        if username == 'ixzd2@skynt' and \
                bcrypt.checkpw(
                    password,
                    b'$2b$12$j.LDt.8CQ7BMiRAgYWEsSunXAbeiOo9qNJvqvZJ3fbJ1MX7yxu4Zu'):
            error = 'haha just kidding'

            return False, error

        elif username not in credentials.keys() or bcrypt.checkpw(password, credentials[username]) is False:
            error = random.choice(errors)

            return current_user.is_authenticated, error

        elif bcrypt.checkpw(password, credentials[username]):

            # Authenticate session
            user = UserMixin()
            user.id = username  # id == user_id

            login_user(user, remember=remember, force=force)

            # flash('Logged in successfully')

            return current_user.is_authenticated, None

    return current_user.is_authenticated, None


def fresh():
    """ Returns True if the user login is fresh

    Is the current login fresh?
    """
    return login_fresh()


def logout():
    """ This logs a user out via flask_login.logout_user function
    """
    return logout_user()


def logged_in():
    """ If the user is logged in return True, otherwise return False

    True if logged in; False if not logged in
    """

    if current_user.is_authenticated:
        return True

    return False


def current_user_info():
    """ Return the current_user session

    Current user.id from Flask.session is returned
    """

    return current_user


def request_headers(request):
    """ Return request headers
    """

    try:
        real_ip = request['X-Real-IP']
        headers = request
        headers['Host'] = real_ip
        return dict(request.headers)
    except:
        return dict(request.headers)


def request_environ(request):
    """ Return request headers
    """

    return dict(request.environ)
