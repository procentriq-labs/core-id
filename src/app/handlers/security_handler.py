from app.models.payloads.authorization_params import AuthorizeParams
from app.models.token.authorization_code_model import AuthorizationCode
from app.handlers.application_handler import ApplicationHandler

from uuid import UUID
import random
import string
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
        if not ApplicationHandler.check_redirect_uri_allowed(client_uuid, params.redirect_uri): raise InvalidRedirectURIException("Provided redirect_uri is not allowed for client.")
        for response_type in params.response_type.split(" "):
            if not ApplicationHandler.check_authorization_flow_allowed(client_uuid, response_type): raise InvalidResponseTypeException(f"Requested response_type `{response_type}` is unsupported or not allowed for client.")
    
    @staticmethod
    def _generate_random_token(length: int) -> str:
        return ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(length))
    
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