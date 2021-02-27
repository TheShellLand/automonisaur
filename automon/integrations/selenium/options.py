import warnings


def default(browser_options):
    browser_options.add_argument('start-maximized')
    return browser_options


def unsafe(browser_options):
    warnings.warn('Certificates are not verified', Warning)
    browser_options.add_argument('--ignore-certificate-errors')
    return browser_options


def nosandbox(browser_options):
    browser_options.add_argument('--no-sandbox')
    return browser_options


def headless(browser_options):
    browser_options.add_argument('headless')
    return browser_options


def noshm(browser_options):
    warnings.warn('Disabled shm will use disk I/O, and will be slow', Warning)
    browser_options.add_argument('--disable-dev-shm-usage')
    return browser_options


def bigshm(browser_options):
    warnings.warn('Big shm not yet implemented', Warning)
    return browser_options


def noinfobars(browser_options):
    browser_options.add_argument("--disable-infobars")
    return browser_options


def noextensions(browser_options):
    browser_options.add_argument("--disable-extensions")
    return browser_options


def nonotifications(browser_options):
    # Pass the argument 1 to allow and 2 to block
    browser_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 1
    })

    return browser_options
