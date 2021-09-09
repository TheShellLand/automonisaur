from automon.integrations.neo4j.cypher import Cypher


# from core.helpers import cryptography


def http_header(headers):
    # [print(x) for x in auth.request_headers(request)]

    # token = cryptography.hash_key(sorted([x for x in headers]))

    args = dict(
        blob=sorted(headers),
        label='Headers'
    )

    Cypher.prepare_dict(**args)
