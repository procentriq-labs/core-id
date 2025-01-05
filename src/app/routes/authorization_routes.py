from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import RedirectResponse
from http import HTTPStatus

from pydantic import BaseModel, Field
from typing import Optional

from app.pages import flask_app
from app.handlers.application_handler import ApplicationHandler

from app.utils.uuid_utils import decode_short_uuid

import logging

logger = logging.getLogger(__name__)

router = APIRouter()

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

@router.get("/authorize")
async def authorize(params: AuthorizeParams = Query()):
    """
    Endpoint to handle OAuth2 authorization requests.
    """
    logger.info(f"Received {params.response_type} authentication request from client {params.client_id}")
    
    try:
        client_id = decode_short_uuid(params.client_id)
    except:
        logger.info(f"Failed to decode client_id {params.client_id}")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Invalid client_id")

    if not ApplicationHandler.check_redirect_uri_allowed(client_id, params.redirect_uri):
        logger.info(f"Invalid redirect_uri {params.redirect_uri} for {params.client_id}")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f"'{params.redirect_uri}' is not a valid redirect_uri for your client.")
    
    for response_type in params.response_type.split(" "):
        if not ApplicationHandler.check_authorization_flow_allowed(client_id, response_type):
            logger.info(f"Received invalid request for disallowed response_type {response_type} from {params.client_id}")
            return RedirectResponse(params.redirect_uri, error="invalid_response_type", error_message=f"'{response_type}' is not a valid response type for your client.", state=params.state)
    
    # TODO validate audience, if provided
    return RedirectResponse(flask_app.url_for("login.signup", _external = False, **params.model_dump()), 302)

