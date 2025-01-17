from fastapi import APIRouter, HTTPException, Form

from app.models.payloads.token_body import TokenRequest, GrantType
from app.models.token.authorization_code_model import AuthorizationCode

from app.handlers.application_handler import ApplicationHandler
from app.handlers.security_handler import SecurityHandler
from app.handlers.user_handler import UserHandler
from app.security.token_handler import TokenHandler

from app.db import get_db_session

from http import HTTPStatus
from typing import Annotated

import logging

logger = logging.getLogger(__name__)

router = APIRouter()

async def get_token_from_authorization_code(b: TokenRequest):
    try:
        client = ApplicationHandler.get_application_by_client_id(b.client_id)
    except:
        logger.info("Failed authorization token exchange request due to invalid client_id")
        raise HTTPException(HTTPStatus.BAD_REQUEST, detail="Invalid client_id")
    
    if ApplicationHandler.check_secret(client, b.client_secret):
        with get_db_session() as s:
            client = s.merge(client)
            auth_code_id, _ = b.code.split('_')
            auth_code: AuthorizationCode = s.query(AuthorizationCode).get(auth_code_id)
            scopes_str = auth_code.scopes if auth_code is not None else None
            audience = auth_code.audience if auth_code is not None else None
            if(SecurityHandler.validate_authorization_code(code=b.code, client_uuid=client.id)):
                
                user = UserHandler.get_user_by_id(auth_code.user_id)

                return_body = TokenHandler.build_token_set(
                    grant_type=b.grant_type,
                    client = client,
                    user = user,
                    scopes_str = scopes_str,
                    audience = audience
                )
                return return_body
            else:
                logger.info("Failed authorization token exchange request due to invalid authorization code")
                raise HTTPException(HTTPStatus.UNAUTHORIZED, detail="Invalid authorization_code")
    else:
        logger.info("Failed authorization token exchange request due to invalid client_secret")
        raise HTTPException(HTTPStatus.UNAUTHORIZED, detail="Invalid client credentials")

@router.post("/oauth2/token")
async def get_token(b: Annotated[TokenRequest, Form()]):
    if b.grant_type == GrantType.AUTHORIZATION_CODE:
        return await get_token_from_authorization_code(b)
    else:
        raise HTTPException(HTTPStatus.NOT_IMPLEMENTED)
    
    