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
from typing import LiteralString
from datetime import datetime, timedelta, timezone

from app.config import load_settings

settings = load_settings()

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
    def generate_authorization_code(client_uuid: UUID, user_uuid: UUID) -> AuthorizationCode:
        LENGTH = settings.security.authorization_code_length
        VALIDITY = settings.security.authorization_code_validity_seconds

        code = SecurityHandler._generate_random_token(LENGTH)
        return AuthorizationCode(
            code = code,
            client_uuid = client_uuid,
            user_uuid = user_uuid,
            exp = datetime.now(timezone.utc) + timedelta(seconds=VALIDITY)
        )
    
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
    def respond_authorize(client_uuid: UUID, user_uuid: UUID, response_types: list[str], redirect_uri: str, state: str):
        response_types_list = response_types.split(' ')

        if("code" not in response_types):
            raise InvalidResponseTypeException()

        SecurityHandler._authorize_validate_redirect_uri_and_response_type(client_uuid=client_uuid, redirect_uri=redirect_uri, response_types=response_types_list)
        
        response_attrs: dict[str, str] = {}

        with get_db_session() as s:
            if("code" in response_types_list):
                authorization_code = SecurityHandler.generate_authorization_code(client_uuid, user_uuid)
                s.add(authorization_code)
                response_attrs["code"] = authorization_code.code
        
        r = PreparedRequest()
        
        r.prepare_url(redirect_uri, params={
            **response_attrs,
            "state": state,
        })
        return redirect(r.url, code=302)
        