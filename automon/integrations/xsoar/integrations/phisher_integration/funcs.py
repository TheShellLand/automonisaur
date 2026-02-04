## DEMISTO MOCK CLASSES FOR LOCAL DEBUGGING
try:
    from automon.integrations.xsoar.local_testing import *
    from automon.integrations.xsoar.demistoWrapper.funcs import *
    # from local_dev.common import *
except:
    pass


def check_spf(message: PhisherMessage) -> PhisherHeader | None:
    searches = message.automon_search_headers('spf=pass')

    for search in searches:
        if searches:
            return search
