import base64
from uuid import UUID
from typing import Generic, TypeVar

T = TypeVar('T')

IDKEY_CLASS_MAP = {}

class UUIDRegistrationError(Exception):
    """Custom error for issues during idkey registration."""
    pass

def short_uuidable(cls):
    """
    Class decorator to register the class by its __idkey__ after the class is fully defined.
    """
    idkey = getattr(cls, '__idkey__', None)
    if idkey is None:
        raise UUIDRegistrationError(f"Class {cls.__name__} does not define an '__idkey__' attribute.")
    
    if idkey in IDKEY_CLASS_MAP:
        raise UUIDRegistrationError(f"idkey '{idkey}' is already registered for {IDKEY_CLASS_MAP[idkey].__name__}")
    
    IDKEY_CLASS_MAP[idkey] = cls
    return cls  # Return the class itself

def encode_short_uuid(raw_uuid: UUID, cls: Generic[T]) -> str:
    key = cls.__idkey__
    u = raw_uuid.bytes  # bytes
    e = base64.urlsafe_b64encode(u) # encode
    return key + "_" + e.decode("utf-8").strip('=') # convert bytes to string and remove fill characters

def decode_short_uuid(uuid_key: str) -> UUID:
    b64encodedUUID = uuid_key.split('_', 1)[1]
    b64encodedUUID = (b64encodedUUID + "=" * (-len(b64encodedUUID)%4)) # add padding if needed
    b = base64.urlsafe_b64decode(b64encodedUUID) # return bytes
    return UUID(bytes=b) 