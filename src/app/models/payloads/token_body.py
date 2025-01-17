from enum import Enum
from pydantic import BaseModel, model_validator
from typing import Optional


class GrantType(str, Enum):
    AUTHORIZATION_CODE = "authorization_code"
    CLIENT_CREDENTIALS = "client_credentials"
    REFRESH_TOKEN = "refresh_token"

class TokenRequest(BaseModel):
    grant_type: GrantType
    code: Optional[str] = None
    refresh_token: Optional[str] = None
    client_id: str
    client_secret: str

    @model_validator(mode="after")
    def validate_grant_type_specific_fields(self):
        """
        Validates required fields based on the grant_type after the object is initialized.
        """
        if self.grant_type == GrantType.AUTHORIZATION_CODE:
            if not self.code:
                raise ValueError("The 'code' field is required for grant_type='authorization_code'")
        elif self.grant_type == GrantType.REFRESH_TOKEN:
            if not self.refresh_token:
                raise ValueError("The 'refresh_token' field is required for grant_type='refresh_token'")
        return self

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    id_token: Optional[str] = None
    token_type: str
    expires_in: int
