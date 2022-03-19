from automon.log import Logging

log = Logging(name='PeopleUrls', level=Logging.ERROR)


class PeopleUrls:
    PEOPLE_API = 'https://people.googleapis.com'
    API_VER = 'v1'
    BASE_URL = f'{PEOPLE_API}/{API_VER}'
    RESOURCE_NAME = 'people'

    sortOrder = [
        'LAST_MODIFIED_ASCENDING',
        'LAST_MODIFIED_DESCENDING',
        'FIRST_NAME_ASCENDING',
        'LAST_NAME_ASCENDING'
    ]

    personFields = [
        'addresses',
        'ageRanges',
        'biographies',
        'birthdays',
        'calendarUrls',
        'clientData',
        'coverPhotos',
        'emailAddresses',
        'events',
        'externalIds',
        'genders',
        'imClients',
        'interests',
        'locales',
        'locations',
        'memberships',
        'metadata',
        'miscKeywords',
        'names',
        'nicknames',
        'occupations',
        'organizations',
        'phoneNumbers',
        'photos',
        'relations',
        'sipAddresses',
        'skills',
        'urls',
        'userDefined'
    ]

    def personFields_toStr(self):
        return ','.join(self.personFields)

    def resourceName(self) -> str:
        log.warn(msg=f'resourceName is deprecieated. Only people/me is valid.')
        return f'{self.RESOURCE_NAME}/me'
