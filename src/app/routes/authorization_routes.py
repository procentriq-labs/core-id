from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import RedirectResponse
from http import HTTPStatus

from app.pages import flask_app
from app.handlers.security_handler import SecurityHandler, InvalidResponseTypeException, InvalidRedirectURIException
from app.models.payloads.authorization_params import AuthorizeParams

from app.utils.uuid_utils import decode_short_uuid
from app.utils.url_utils import amend_get_params

import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/authorize")
async def authorize(params: AuthorizeParams = Query()):
    """
    Endpoint to handle OAuth2 authorization requests.
    """
    logger.info(f"Received {params.response_type} authentication request from client {params.client_id}")

    # TODO in future, if scope offline_access (= refresh token) is requested, get user consent to stay logged in with application
    
    try:
        client_id = decode_short_uuid(params.client_id)
        SecurityHandler.authorize_validate_params(client_id, params)
        return RedirectResponse(flask_app.url_for("login.login", _external = False, **params.model_dump()), 302)
    except ValueError:
        logger.info(f"Failed to decode client_id {params.client_id}")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Invalid client_id")
    except InvalidRedirectURIException:
        logger.info(f"Invalid redirect_uri {params.redirect_uri} for {params.client_id}")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f"'{params.redirect_uri}' is not a valid redirect_uri for your client.")
    except InvalidResponseTypeException as e:
        logger.info(f"Received invalid request for disallowed response_type from {params.client_id}: {str(e)}")
        return RedirectResponse(amend_get_params(url=params.redirect_uri, d=dict(error="invalid_response_type", error_message=str(e), state=params.state)))

