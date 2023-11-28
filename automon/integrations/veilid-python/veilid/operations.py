from enum import StrEnum
from typing import Self


class Operation(StrEnum):
    CONTROL = "Control"
    GET_STATE = "GetState"
    ATTACH = "Attach"
    DETACH = "Detach"
    NEW_PRIVATE_ROUTE = "NewPrivateRoute"
    NEW_CUSTOM_PRIVATE_ROUTE = "NewCustomPrivateRoute"
    IMPORT_REMOTE_PRIVATE_ROUTE = "ImportRemotePrivateRoute"
    RELEASE_PRIVATE_ROUTE = "ReleasePrivateRoute"
    APP_CALL_REPLY = "AppCallReply"
    NEW_ROUTING_CONTEXT = "NewRoutingContext"
    ROUTING_CONTEXT = "RoutingContext"
    OPEN_TABLE_DB = "OpenTableDb"
    DELETE_TABLE_DB = "DeleteTableDb"
    TABLE_DB = "TableDb"
    TABLE_DB_TRANSACTION = "TableDbTransaction"
    GET_CRYPTO_SYSTEM = "GetCryptoSystem"
    BEST_CRYPTO_SYSTEM = "BestCryptoSystem"
    CRYPTO_SYSTEM = "CryptoSystem"
    VERIFY_SIGNATURES = "VerifySignatures"
    GENERATE_SIGNATURES = "GenerateSignatures"
    GENERATE_KEY_PAIR = "GenerateKeyPair"
    NOW = "Now"
    DEBUG = "Debug"
    VEILID_VERSION_STRING = "VeilidVersionString"
    VEILID_VERSION = "VeilidVersion"


class RoutingContextOperation(StrEnum):
    INVALID_ID = "InvalidId"
    RELEASE = "Release"
    WITH_DEFAULT_SAFETY = "WithDefaultSafety"
    WITH_SAFETY = "WithSafety"
    WITH_SEQUENCING = "WithSequencing"
    SAFETY = "Safety"
    APP_CALL = "AppCall"
    APP_MESSAGE = "AppMessage"
    CREATE_DHT_RECORD = "CreateDhtRecord"
    OPEN_DHT_RECORD = "OpenDhtRecord"
    CLOSE_DHT_RECORD = "CloseDhtRecord"
    DELETE_DHT_RECORD = "DeleteDhtRecord"
    GET_DHT_VALUE = "GetDhtValue"
    SET_DHT_VALUE = "SetDhtValue"
    WATCH_DHT_VALUES = "WatchDhtValues"
    CANCEL_DHT_WATCH = "CancelDhtWatch"


class TableDbOperation(StrEnum):
    INVALID_ID = "InvalidId"
    RELEASE = "Release"
    GET_COLUMN_COUNT = "GetColumnCount"
    GET_KEYS = "GetKeys"
    TRANSACT = "Transact"
    STORE = "Store"
    LOAD = "Load"
    DELETE = "Delete"


class TableDbTransactionOperation(StrEnum):
    INVALID_ID = "InvalidId"
    COMMIT = "Commit"
    ROLLBACK = "Rollback"
    STORE = "Store"
    DELETE = "Delete"


class CryptoSystemOperation(StrEnum):
    INVALID_ID = "InvalidId"
    RELEASE = "Release"
    CACHED_DH = "CachedDh"
    COMPUTE_DH = "ComputeDh"
    RANDOM_BYTES = "RandomBytes"
    DEFAULT_SALT_LENGTH = "DefaultSaltLength"
    HASH_PASSWORD = "HashPassword"
    VERIFY_PASSWORD = "VerifyPassword"
    DERIVE_SHARED_SECRET = "DeriveSharedSecret"
    RANDOM_NONCE = "RandomNonce"
    RANDOM_SHARED_SECRET = "RandomSharedSecret"
    GENERATE_KEY_PAIR = "GenerateKeyPair"
    GENERATE_HASH = "GenerateHash"
    VALIDATE_KEY_PAIR = "ValidateKeyPair"
    VALIDATE_HASH = "ValidateHash"
    DISTANCE = "Distance"
    SIGN = "Sign"
    VERIFY = "Verify"
    AEAD_OVERHEAD = "AeadOverhead"
    DECRYPT_AEAD = "DecryptAead"
    ENCRYPT_AEAD = "EncryptAead"
    CRYPT_NO_AUTH = "CryptNoAuth"


class RecvMessageType(StrEnum):
    RESPONSE = "Response"
    UPDATE = "Update"
