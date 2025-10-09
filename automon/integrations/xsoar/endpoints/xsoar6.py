class V1:
    v1: str = f''


class Reports:
    reports: str = f'/reports'


class Files:
    """
    https://cortex-panw.stoplight.io/docs/cortex-xsoar-6/43ko2zqvunjz0-download-file

    """

    def __init__(self):
        pass

    def get_by_entryid(self, entryid: str) -> str:
        return f'/entry/download/{entryid}'


class Incidents:

    def __init__(self):
        pass

    @property
    def create_incident(self):
        """
        IncidentWrapper is an extension of the Incident entity, which includes an additional field of changed-status for the web client

        ShardID
        integer<int64>
        account
        string
        Account holds the tenant name so that slicing and dicing on the master can leverage bleve

        activated
        string<date-time>
        When was this activated

        activatingingUserId
        string
        The user that activated this investigation

        allRead
        boolean
        allReadWrite
        boolean
        attachment
        array[Attachment ...]
        Attachments

        description
        string
        isTempPath
        boolean
        name
        string
        path
        string
        showMediaFile
        boolean
        type
        string
        autime
        integer<int64>
        AlmostUniqueTime is an attempt to have a unique sortable ID for an incident

        cacheVersn
        integer<int64>
        canvases
        array[string]
        Canvases of the incident

        category
        string
        Category

        changeStatus
        string
        closeNotes
        string
        Notes for closing the incident

        closeReason
        string
        The reason for closing the incident (select from existing predefined values)

        closed
        string<date-time>
        When was this closed

        closingUserId
        string
        The user ID that closed this investigation

        created
        string<date-time>
        dbotCreatedBy
        string
        Who has created this event - relevant only for manual incidents

        dbotCurrentDirtyFields
        array[string]
        For mirroring, manage a list of current dirty fields so that we can send delta to outgoing integration

        dbotDirtyFields
        array[string]
        For mirroring, manage a list of dirty fields to not override them from the source of the incident

        dbotMirrorDirection
        string
        DBotMirrorDirection of how to mirror the incident (in/out/both)

        dbotMirrorId
        string
        DBotMirrorID of a remote system we are syncing with

        dbotMirrorInstance
        string
        DBotMirrorInstance name of a mirror integration instance

        dbotMirrorLastSync
        string<date-time>
        The last time we synced this incident even if we did not update anything

        dbotMirrorTags
        array[string]
        The entry tags I want to sync to remote system

        details
        string
        The details of the incident - reason, etc.

        droppedCount
        integer<int64>
        DroppedCount ...

        dueDate
        string<date-time>
        SLA

        feedBased
        boolean
        If this incident was triggered by a feed job

        hasRole
        boolean
        Internal field to make queries on role faster

        highlight
        dictionary[string, array]
        string
        id
        string
        indexName
        string
        insights
        integer
        investigationId
        string
        Investigation that was opened as a result of the incoming event

        isDebug
        boolean
        IsDebug ...

        isPlayground
        boolean
        IsPlayGround

        labels
        array[Label ...]
        Labels related to incident - each label is composed of a type and value

        type
        string
        value
        string
        lastJobRunTime
        string<date-time>
        If this incident was triggered by a job, this would be the time the previous job started

        lastOpen
        string<date-time>
        linkedCount
        integer<int64>
        LinkedCount ...

        linkedIncidents
        array[string]
        LinkedIncidents incidents that were marked as linked by user

        modified
        string<date-time>
        name
        string
        Incident Name - given by user

        notifyTime
        string<date-time>
        Incdicates when last this field was changed with a value that supposed to send a notification

        numericId
        integer<int64>
        occurred
        string<date-time>
        When this incident has really occurred

        openDuration
        integer<int64>
        Duration incident was open

        owner
        string
        The user who owns this incident

        parent
        string
        Parent

        phase
        string
        Phase

        playbookId
        string
        The associated playbook for this incident

        previousAllRead
        boolean
        previousAllReadWrite
        boolean
        previousRoles
        array[string]
        Do not change this field manually

        primaryTerm
        integer<int64>
        rawCategory
        string
        rawCloseReason
        string
        The reason for closing the incident (select from existing predefined values)

        rawJSON
        string
        rawName
        string
        Incident RawName

        rawPhase
        string
        RawPhase

        rawType
        string
        Incident raw type

        reason
        string
        The reason for the resolve

        reminder
        string<date-time>
        When if at all to send a reminder

        roles
        array[string]
        The role assigned to this investigation

        runStatus
        string
        RunStatus of a job

        sequenceNumber
        integer<int64>
        severity
        number<double>
        Severity is the incident severity

        >= 0
        Example:
        4
        Multiple of:
        4
        sizeInBytes
        integer<int64>
        sla
        number<double>
        SLAState is the incident sla at closure time, in minutes.

        sortValues
        array[string]
        sourceBrand
        string
        SourceBrand ...

        sourceInstance
        string
        SourceInstance ...

        status
        number<double>
        IncidentStatus is the status of the incident

        >= 0
        <= 2
        Example:
        2
        syncHash
        string
        todoTaskIds
        array[string]
        ToDoTaskIDs list of to do task ids

        type
        string
        Incident type

        version
        integer<int64>
        xsoarHasReadOnlyRole
        boolean
        xsoarPreviousReadOnlyRoles
        array[string]
        xsoarReadOnlyRoles
        array[string]
        """
        return f'incident'

    def delete_incident_batch(self):
        """
        {
            "CustomFields": {
                "property1": {},
                "property2": {}
            },
            "all": true,
            "closeNotes": "string",
            "closeReason": "string",
            "columns": [
                "string"
            ],
            "data": {
                "property1": {},
                "property2": {}
            },
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
            "force": true,
            "ids": [
                "string"
            ],
            "line": "string",
            "originalIncidentId": "string",
            "overrideInvestigation": true
        }

        """
        return f'incident/batchDelete'

    def get_by_id(self, id: int):
        return f'incident/load/{id}'

    @property
    def search_incident(self):
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
        return f'/incidents/search'


class IncidentResponse:
    pass
