from pydantic import BaseModel, Field
from typing import Optional

class AuthorizeParams(BaseModel):
    client_id: str = Field(
        ...,  # Required
        description="Application's unique ID."
    )
    audience: Optional[str] = Field(
        None,
        description="Identifier of the target API."
    )
    scope: Optional[str] = Field(
        None,
        description="Requested permissions, separated by spaces."
    )
    response_type: str = Field(
        ...,  # Required
        description="OAuth2 flow type (e.g., 'code')."
    )
    redirect_uri: str = Field(
        ..., # Required
        description="URL to redirect after authorization."
    )
    state: Optional[str] = Field(
        None,
        description="Value to prevent CSRF attacks."
    )
    # invitation: Optional[str] = Field(
    #     None,
    #     description="Invitation ID for adding users to organizations."
    # )
    # organization: Optional[str] = Field( # Use for invitations 
    #     None,
    #     description="Organization ID for authentication."
    # )