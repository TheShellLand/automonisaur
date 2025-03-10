import automon.helpers.cryptography

from automon.integrations.neo4jWrapper.cypher import Cypher


# from core.helpers import cryptography


def http_header(headers):
    # [print(x) for x in auth.request_headers(request)]

    # token = automon.helpers.cryptography.Hashlib.md5(sorted([x for x in headers]))

    args = dict(
        blob=sorted(headers),
        label='Headers'
    )

    Cypher.prepare_dict(**args)
