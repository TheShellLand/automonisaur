from automon.integrations.neo4j.cypher import Cypher


# from core.helpers import crypto


def http_header(headers):
    # [print(x) for x in auth.request_headers(request)]

    # token = crypto.hash_key(sorted([x for x in headers]))

    args = dict(
        blob=sorted(headers),
        label='Headers'
    )

    Cypher.prepare_dict(**args)
