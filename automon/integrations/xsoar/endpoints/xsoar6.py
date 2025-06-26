class V1:
    v1: str = f''


class Reports:
    reports: str = f'/reports'


class Incidents:
    """
    https://cortex-panw.stoplight.io/docs/cortex-xsoar-6/4ewvqjrm5eps4-search-incidents-by-filter

    {
      "filter": {
        "Cache": {
          "property1": [
            "string"
          ],
          "property2": [
            "string"
          ]
        },
        "accounts": {
          "property1": {},
          "property2": {}
        },
        "andOp": true,
        "category": [
          "string"
        ],
        "details": "string",
        "fields": [
          "string"
        ],
        "files": [
          "string"
        ],
        "filterobjectquery": "string",
        "fromActivatedDate": "2019-08-24T14:15:22Z",
        "fromClosedDate": "2019-08-24T14:15:22Z",
        "fromDate": "2019-08-24T14:15:22Z",
        "fromDateLicense": "2019-08-24T14:15:22Z",
        "fromDueDate": "2019-08-24T14:15:22Z",
        "fromReminder": "2019-08-24T14:15:22Z",
        "id": [
          "string"
        ],
        "ignoreWorkers": true,
        "includeTmp": true,
        "investigation": [
          "string"
        ],
        "level": [
          4
        ],
        "name": [
          "string"
        ],
        "notCategory": [
          "string"
        ],
        "notInvestigation": [
          "string"
        ],
        "notStatus": [
          2
        ],
        "page": -9007199254740991,
        "parent": [
          "string"
        ],
        "period": {
          "by": "string",
          "byFrom": "string",
          "byTo": "string",
          "field": "string",
          "fromValue": "string",
          "toValue": "string"
        },
        "query": "string",
        "reason": [
          "string"
        ],
        "searchAfter": [
          "string"
        ],
        "searchAfterElastic": [
          "string"
        ],
        "searchAfterMap": {
          "property1": [
            "string"
          ],
          "property2": [
            "string"
          ]
        },
        "searchAfterMapOrder": {
          "property1": -9007199254740991,
          "property2": -9007199254740991
        },
        "searchBefore": [
          "string"
        ],
        "searchBeforeElastic": [
          "string"
        ],
        "size": -9007199254740991,
        "sort": [
          {
            "asc": true,
            "field": "string",
            "fieldType": "string"
          }
        ],
        "status": [
          2
        ],
        "systems": [
          "string"
        ],
        "timeFrame": -9007199254740991,
        "toActivatedDate": "2019-08-24T14:15:22Z",
        "toClosedDate": "2019-08-24T14:15:22Z",
        "toDate": "2019-08-24T14:15:22Z",
        "toDueDate": "2019-08-24T14:15:22Z",
        "toReminder": "2019-08-24T14:15:22Z",
        "totalOnly": true,
        "trim_events": -9007199254740991,
        "type": [
          "string"
        ],
        "urls": [
          "string"
        ],
        "users": [
          "string"
        ]
      },
      "userFilter": true
    }
    """
    incidents: str = f'/incidents/search'

    def __init__(self):
        pass

    def get_by_id(self, id: int):
        return f'incident/load/{id}'
