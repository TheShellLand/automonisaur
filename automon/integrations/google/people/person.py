from enum import Enum

from automon.log import Logging

log = Logging(level=Logging.DEBUG)


class AgeRange(Enum):
    """Please use person.ageRanges instead"""
    log.warn(DeprecationWarning)

    AGE_RANGE_UNSPECIFIED = 'AGE_RANGE_UNSPECIFIED'
    LESS_THAN_EIGHTEEN = 'LESS_THAN_EIGHTEEN'
    EIGHTEEN_TO_TWENTY = 'EIGHTEEN_TO_TWENTY'
    TWENTY_ONE_OR_OLDER = 'TWENTY_ONE_OR_OLDER'


class ContentType(Enum):
    """
    :CONTENT_TYPE_UNSPECIFIED: Unspecified
    :TEXT_PLAIN: Plain text.
    :TEXT_HTML: HTML text.
    """
    CONTENT_TYPE_UNSPECIFIED = 'CONTENT_TYPE_UNSPECIFIED'
    TEXT_PLAIN = 'TEXT_PLAIN'
    TEXT_HTML = 'TEXT_HTML'


class Date(object):
    """
    :year: Year of the date. Must be from 1 to 9999, or 0 to specify a date without a year.
    :month: Month of a year. Must be from 1 to 12, or 0 to specify a year without a month and day.
    :day: Day of a month. Must be from 1 to 31 and valid for the year and month, or 0 to specify a
        year by itself or a year and month where the day isn't significant.
    """
    year: int
    month: int
    dat: int


class KeywordType(Enum):
    TYPE_UNSPECIFIED = 'TYPE_UNSPECIFIED'
    OUTLOOK_BILLING_INFORMATION = 'OUTLOOK_BILLING_INFORMATION'
    OUTLOOK_DIRECTORY_SERVER = 'OUTLOOK_DIRECTORY_SERVER'
    OUTLOOK_KEYWORD = 'OUTLOOK_KEYWORD'
    OUTLOOK_MILEAGE = 'OUTLOOK_MILEAGE'
    OUTLOOK_PRIORITY = 'OUTLOOK_PRIORITY'
    OUTLOOK_SENSITIVITY = 'OUTLOOK_SENSITIVITY'
    OUTLOOK_SUBJECT = 'OUTLOOK_SUBJECT'
    OUTLOOK_USER = 'OUTLOOK_USER'
    HOME = 'HOME'
    WORK = 'WORK'
    OTHER = 'OTHER'


class NicknameType(Enum):
    """
    :DEFAULT: Generic nickname.
    :MAIDEN_NAME: (depreciated)
    :INITIALS: (depreciated)
    :GPLUS: (depreciated)
    :OTHER_NAME: (depreciated)
    :ALTERNATE_NAME: (depreciated)
    :SHORT_NAME: (depreciated)
    """
    DEFAULT = 'DEFAULT'
    MAIDEN_NAME = 'MAIDEN_NAME'
    INITIALS = 'INITIALS'
    GPLUS = 'GPLUS'
    OTHER_NAME = 'OTHER_NAME'
    ALTERNATE_NAME = 'ALTERNATE_NAME'
    SHORT_NAME = 'SHORT_NAME'


class ObjectType(Enum):
    OBJECT_TYPE_UNSPECIFIED = 'OBJECT_TYPE_UNSPECIFIED'
    PERSON = 'PERSON'
    PAGE = 'PAGE'


class SourceType(Enum):
    SOURCE_TYPE_UNSPECIFIED = 'SOURCE_TYPE_UNSPECIFIED'
    ACCOUNT = 'ACCOUNT'
    PROFILE = 'PROFILE'
    DOMAIN_PROFILE = 'DOMAIN_PROFILE'
    CONTACT = 'CONTACT'
    OTHER_CONTACT = 'OTHER_CONTACT'
    DOMAIN_CONTACT = 'DOMAIN_CONTACT'


class UserType(Enum):
    USER_TYPE_UNKNOWN = 'USER_TYPE_UNKNOWN'
    GOOGLE_USER = 'GOOGLE_USER'
    GPLUS_USER = 'GPLUS_USER'
    GOOGLE_APPS_USER = 'GOOGLE_APPS_USER'


class ProfileMetadata(object):
    objectType: ObjectType
    userTypes: [UserType]


class Source(object):
    type: SourceType
    etag: str
    updateTime: str
    profileMetadata: ProfileMetadata


class FieldMetadata(object):
    primary: bool
    sourcePrimary: bool
    verified: bool
    source: Source


class FileMetadata(object):
    primary: bool
    sourcePrimary: bool
    verified: bool
    source: Source


class Address(object):
    metadata: FieldMetadata
    formattedValue: str
    type: str
    formattedType: str
    poBox: str
    streetAddress: str
    extendedAddress: str
    city: str
    region: str
    postalCode: str
    country: str
    countryCode: str


class AgeRangeType(object):
    metadata: FieldMetadata
    ageRange: AgeRange


class Biography(object):
    metadata: FieldMetadata
    value: str
    contentType: ContentType


class Birthday(object):
    metadata: FieldMetadata
    date: Date
    text: str


class BraggingRights(object):
    """
    :metadata: Metadata about the bragging rights.
    :value: The bragging rights; for example, climbed mount everest
    """
    metadata: FieldMetadata
    value: str


class ContactGroupMembership(object):
    """
    :contactGroupId: (depreciated) Output only. The contact group ID for the contact group membership.
    :contactGroupResourceName: The resource name for the contact group, assigned by the server. An ASCII
        string, in the form of contactGroups/{contactGroupId}. Only contactGroupResourceName can be used for
        modifying memberships. Any contact group membership can be removed, but only user group or "myContacts"
        or "starred" system groups memberships can be added. A contact must always have at least one contact
        group membership.
    """
    contactGroupId: str
    contactGroupResourceName: str


class ClientData(object):
    metadata: FileMetadata
    key: str
    value: str


class CoverPhoto(object):
    metadata: FieldMetadata
    url: str
    default: bool


class CalendarUrl(object):
    """
    :formattedType: Output only. The type of the calendar URL translated and formatted in the
        viewer's account locale or the Accept-Language HTTP header locale.
    """
    metadata: FieldMetadata
    url: str
    type: str
    formattedType: str


class DomainMembership(object):
    """
    :inViewerDomain: True if the person is in the viewer's Google Workspace domain.
    """
    inViewerDomain: bool


class EmailAddress(object):
    metadata: FieldMetadata
    value: str
    type: str
    formattedType: str
    displayName: str


class Event(object):
    metadata: FieldMetadata
    date: Date
    type: str
    formattedType: str


class ExternalId(object):
    metadata: FieldMetadata
    value: str
    type: str
    formattedType: str


class FileAs(object):
    metadata: FieldMetadata
    value: str


class Gender(object):
    metadata: FieldMetadata
    value: str
    formattedValue: str
    addressMeAs: str


class ImClient(object):
    metadata: FieldMetadata
    username: str
    type: str
    formattedType: str
    protocol: str
    formattedProtocol: str


class Interest(object):
    metadata: FieldMetadata
    value: str


class Locale(object):
    metadata: FieldMetadata
    value: str


class Location(object):
    metadata: {
        FieldMetadata
    }
    value: str
    type: str
    current: bool
    buildingId: str
    floor: str
    floorSection: str
    deskCode: str


class Membership(object):
    """
    :metadata: Metadata about the membership.
    :contactGroupMembership: The contact group membership.
    :domainMembership: Output only. The domain membership.
    """
    metadata: {
        FieldMetadata
    }
    contactGroupMembership: {
        ContactGroupMembership
    }
    domainMembership: {
        DomainMembership
    }


class MiscKeyword(object):
    metadata: {
        FieldMetadata
    }
    value: str
    type: KeywordType
    formattedType: str


class Name(object):
    metadata: {
        FieldMetadata
    }
    displayName: str
    displayNameLastFirst: str
    unstructuredName: str
    familyName: str
    givenName: str
    middleName: str
    honorificPrefix: str
    honorificSuffix: str
    phoneticFullName: str
    phoneticFamilyName: str
    phoneticGivenName: str
    phoneticMiddleName: str
    phoneticHonorificPrefix: str
    phoneticHonorificSuffix: str


class Nickname(object):
    metadata: {
        FieldMetadata
    }
    value: str
    type: NicknameType


class Occupation(object):
    metadata: {
        FieldMetadata
    }
    value: str


class Organization(object):
    metadata: {
        FieldMetadata
    }
    type: str
    formattedType: str
    startDate: {
        Date
    }
    endDate: {
        Date
    }
    current: bool
    name: str
    phoneticName: str
    department: str
    title: str
    jobDescription: str
    symbol: str
    domain: str
    location: str
    costCenter: str
    fullTimeEquivalentMillipercent: int


class PersonMetadata(object):
    soures: [Source]
    previousResourceNames: [str]
    linkedPeopleResourceNames: [str]
    deleted: bool
    objectType: ObjectType


class PhoneNumber(object):
    metadata: {
        FieldMetadata
    }
    value: str
    canonicalForm: str
    type: str
    formattedType: str


class Photo(object):
    metadata: {
        FieldMetadata
    }
    url: str
    default: bool


class Relation(object):
    metadata: {
        FieldMetadata
    }
    person: str
    type: str
    formattedType: str


class RelationshipInterest(object):
    log.warn(DeprecationWarning)

    metadata: {
        FieldMetadata
    }
    value: str
    formattedValue: str


class RelationshipStatus(object):
    log.warn(DeprecationWarning)

    metadata: {
        FieldMetadata
    }
    value: str
    formattedValue: str


class Residence(object):
    log.warn(DeprecationWarning)

    metadata: {
        FieldMetadata
    }
    value: str
    current: bool


class SipAddress(object):
    metadata: {
        FieldMetadata
    }
    value: str
    type: str
    formattedType: str


class Skill(object):
    metadata: {
        FieldMetadata
    }
    value: str


class Tagline(object):
    log.warn(DeprecationWarning)

    metadata: {
        FieldMetadata
    }
    value: str


class Url(object):
    metadata: {
        FieldMetadata
    }
    value: str
    type: str
    formattedType: str


class UserDefined(object):
    metadata: {
        FieldMetadata
    }
    key: str
    value: str


class Person(object):
    resourceName: str
    etag: str
    metadata: PersonMetadata
    addresses: [Address]
    ageRange: AgeRange
    ageRanges: [AgeRangeType]
    biographies: [Biography]
    birthdays: [Birthday]
    braggingRights: [BraggingRights]
    calendarUrls: [CalendarUrl]
    clientData: [ClientData]
    coverPhotos: [CoverPhoto]
    emailAddresses: [EmailAddress]
    events: [Event]
    externalIds: [ExternalId]
    fileAses: [FileAs]
    genders: [Gender]
    imClients: [ImClient]
    interests: [Interest]
    locales: [Locale]
    locations: [Location]
    memberships: [Membership]
    miscKeywords: [MiscKeyword]
    names: [Name]
    nicknames: [Nickname]
    occupations: [Occupation]
    organizations: [Organization]
    phoneNumbers: [PhoneNumber]
    photos: [Photo]
    relations: [Relation]
    relationshipInterests: [RelationshipInterest]
    relationshipStatuses: [RelationshipStatus]
    residences: [Residence]
    sipAddresses: [SipAddress]
    skills: [Skill]
    taglines: [Tagline]
    urls: [Url]
    userDefined: [UserDefined]

    def __init__(self, contact: dict):
        """People Resource"""
        self.__dict__.update(contact)

    def __repr__(self):
        return f'{[x for x in self.get_names() for x in x.values() if isinstance(x, str)][-1]}'

    def to_dict(self):
        return dict(self.__dict__)

    def get_biographies(self):
        return self.__dict__.get('biographies', [])

    def get_memberships(self):
        return self.__dict__.get('memberships', [])

    def get_names(self):
        return self.__dict__.get('names', [])

    def get_phoneNumbers(self):
        return self.__dict__.get('phoneNumbers', [])
