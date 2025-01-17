from app.models.payloads.authorization_params import AuthorizeParams
from app.models.token.authorization_code_model import AuthorizationCode
from app.models.token.verify_email_token_model import VerifyEmailToken
from app.handlers.application_handler import ApplicationHandler
from app.db import get_db_session

from werkzeug.utils import redirect
from requests.models import PreparedRequest
from uuid import UUID
import random
import string
from base64 import b64decode, b64encode
from typing import LiteralString, Tuple
from datetime import datetime, timedelta, timezone

from app.config import load_settings

import logging

settings = load_settings()
logger = logging.getLogger(__name__)

class InvalidRedirectURIException(Exception):
    """Exception raised when provided `redirect_uri` is not allowed for client."""
    def __init__(self, message):
        super().__init__(message)

class InvalidResponseTypeException(Exception):
    """Exception raised when requested response_type is unsupported or not allowed for client."""
    def __init__(self, message):
        super().__init__(message)

class SecurityHandler:
    @staticmethod
    def _authorize_validate_redirect_uri_and_response_type(client_uuid: UUID, redirect_uri: str, response_types: list[str]):
        if not ApplicationHandler.check_redirect_uri_allowed(client_uuid, redirect_uri): raise InvalidRedirectURIException("Provided redirect_uri is not allowed for client.")
        for response_type in response_types:
            if not ApplicationHandler.check_authorization_flow_allowed(client_uuid, response_type): raise InvalidResponseTypeException(f"Requested response_type `{response_type}` is unsupported or not allowed for client.")

    @staticmethod
    def authorize_validate_params(client_uuid: UUID, params: AuthorizeParams):
        """
        Validates the authorization parameters for a given client.

        This function checks whether the redirect URI is allowed for the specified
        client and validates that the requested authorization flows are permitted.

        Args:
            client_uuid (UUID): The unique identifier of the client application.
            params (AuthorizeParams): The authorization parameters, including the
                redirect URI and response type(s).

        Raises:
            InvalidRedirectURIException: If the redirect URI is not allowed for the client.
            InvalidResponseTypeException: If any of the requested response types are not permitted for the client.
        """
        SecurityHandler._authorize_validate_redirect_uri_and_response_type(client_uuid=client_uuid, redirect_uri=params.redirect_uri, response_types=params.response_type.split(' '))
    
    @staticmethod
    def _generate_random_token(length: int, alphabet: LiteralString = string.ascii_letters + string.digits) -> str:
        return ''.join(random.SystemRandom().choice(alphabet) for _ in range(length))
    
    @staticmethod
    def generate_authorization_code(client_uuid: UUID, user_uuid: UUID, scopes_str: str = "", audience: str = "") -> Tuple[AuthorizationCode, str]:
        LENGTH = settings.security.authorization_code_length
        VALIDITY = settings.security.authorization_code_validity_seconds

        code_identifier = SecurityHandler._generate_random_token(8) # hard-coded
        code_plaintext = SecurityHandler._generate_random_token(LENGTH)

        codeb64 = b64encode(code_plaintext.encode("utf-8")).decode("utf-8")
        code_str = f"{code_identifier}_{codeb64}"

        auth_code_obj = AuthorizationCode(
            code_identifier=code_identifier,
            code = code_plaintext,
            client_uuid = client_uuid,
            user_uuid = user_uuid,
            exp = datetime.now(timezone.utc) + timedelta(seconds=VALIDITY),
            scopes= scopes_str,
            audience=audience,
        )

        return (auth_code_obj, code_str)

    @staticmethod
    def validate_authorization_code(code: str, client_uuid: UUID) -> bool:
        code_identifier, code_plaintext_b64 = code.split("_")

        base64_bytes = code_plaintext_b64.encode("utf-8")
        code_plaintext = b64decode(base64_bytes).decode("utf-8")

        with get_db_session() as s:
            try:
                authorization_code = s.query(AuthorizationCode).filter_by(
                    code_identifier = code_identifier,
                    application_id = client_uuid,
                ).one()
                if (authorization_code._cyrpt_context.verify(code_plaintext, authorization_code.hashed_code)):
                    s.delete(authorization_code)
                    if authorization_code.expires_at > datetime.now(tz=None): #need timezone none (utc) cause expires_at is not offset_aware
                        return True
                    logger.info(f"Failed to verify authorization code for client_id {str(client_uuid)}: Token expired")
                    return False
                else:
                    logger.info(f"Failed to verify authorization code for client_id {str(client_uuid)}: Token invalid")
                    return False
            except:
                logger.info(f"Failed to verify authorization code for client_id {str(client_uuid)}: Didn't find code with id {code_identifier} for client.")
                return False
    
    @staticmethod
    def generate_verify_email_token(user_uuid: UUID) -> VerifyEmailToken:
        VALIDITY = settings.security.email_verification_code_validity_seconds
        
        token = SecurityHandler._generate_random_token(6, alphabet=string.digits)

        return VerifyEmailToken(
            user_uuid = user_uuid,
            token = token,
            exp = datetime.now(timezone.utc) + timedelta(seconds=VALIDITY),
        )
    
    @staticmethod
    def validate_user_otp(user_uuid: UUID, otp: str) -> bool:
        with get_db_session() as s:
            token = s.query(VerifyEmailToken).get((otp, user_uuid))
            if token is not None:
                s.delete(token)
                if token.expires_at > datetime.now(tz=None): #need timezone none (utc) cause expires_at is not offset_aware
                    return True
        return False
    
    @staticmethod
    def respond_authorize(client_uuid: UUID, user_uuid: UUID, response_types: list[str], redirect_uri: str, state: str, scopes_str: str = "", audience: str = ""):
        response_types_list = response_types.split(' ')

        if("code" not in response_types):
            raise InvalidResponseTypeException()

        SecurityHandler._authorize_validate_redirect_uri_and_response_type(client_uuid=client_uuid, redirect_uri=redirect_uri, response_types=response_types_list)
        
        response_attrs: dict[str, str] = {}

        with get_db_session() as s:
            if("code" in response_types_list):
                authorization_code_obj, authorization_code_str = SecurityHandler.generate_authorization_code(client_uuid, user_uuid, scopes_str, audience)
                logger.debug(f"code identifier: {authorization_code_obj.code_identifier}")
                s.add(authorization_code_obj)
                response_attrs["code"] = authorization_code_str
        
        r = PreparedRequest()
        
        r.prepare_url(redirect_uri, params={
            **response_attrs,
            "state": state,
        })
        return redirect(r.url, code=302)
        