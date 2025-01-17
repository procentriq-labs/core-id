from app.models.payloads.token_body import GrantType, TokenResponse

from app.models.application.application_model import Application
from app.models.organization.user_model import User
from app.models.token.refresh_token_model import RefreshToken

from app.security.key_management import KeyManager
from app.security.jwt_handler import generate_jwt
from app.handlers.security_handler import SecurityHandler

from app.db import get_db_session
from uuid import UUID

from app.config import load_settings

settings = load_settings()

key_manager = KeyManager()

class TokenHandler:
    @staticmethod
    def build_token_set(grant_type: GrantType, client: Application, user: User | None = None, scopes_str: str = "", audience: str | None = None) -> TokenResponse:
        """
        Assumes request is authorized.
        """
        JWT_ALG = "RS256"
        ISSUER = settings.app_host_public_url
        ACCESS_TOKEN_LIFESPAN = settings.security.access_token_validity_seconds
        IDTOKEN_LIFESPAN = settings.security.idtoken_validity_seconds
        REFRESH_TOKEN_LENGTH = settings.security.refresh_token_length
        REFRESH_TOKEN_LIFESPAN = settings.security.refresh_token_validity_seconds

        scopes = scopes_str.split(' ')
        # TODO !! filter scopes, only include ones that user/ client is authorized for

        # TODO validate audience against requested resources..?!

        with get_db_session() as s:
            client = s.merge(client)
            client_uuid = client.id
            client_key = client.get_id()

            user = None if user is not None else s.merge(user)
            user_key = None if user is None else user.get_id()
            user_uuid = None if user is None else user.id
            org_key = None if user is None or user.organization_id is None else user.organization_id # TODO this should be encoded
            access_token_is_openid = False

        tokens: dict[str, str] = {
            'token_type': 'Bearer',
            'expires_in': ACCESS_TOKEN_LIFESPAN,
        }

        if(grant_type == GrantType.AUTHORIZATION_CODE and 'offline_access' in scopes) or grant_type == GrantType.REFRESH_TOKEN:
            refresh_token = TokenHandler._build_refresh_token(
                client_uuid = client_uuid,
                user_uuid = user_uuid,
                length = REFRESH_TOKEN_LENGTH,
                scopes_str = scopes_str,
                lifespan = REFRESH_TOKEN_LIFESPAN,
            )
            tokens['refresh_token'] = refresh_token

        if(grant_type != GrantType.CLIENT_CREDENTIALS):
            if(user is not None):
                with get_db_session() as s:
                    client = s.merge(client)
                    user = s.merge(user)

                    if("openid" in scopes):
                        access_token_is_openid = True

                        # Generate IDToken
                        idtoken = TokenHandler._build_id_token(
                            client_key = client_key,
                            user = user,
                            scopes = scopes,
                            issuer = ISSUER,
                            lifespan = IDTOKEN_LIFESPAN,
                            jwt_alg = JWT_ALG,
                        )
                        tokens['id_token'] = idtoken
        
        # build access token
        access_token = TokenHandler._build_access_token(
            audience = audience,
            client_key = client_key,
            user_key = user_key,
            org_key = org_key,
            grant_type = grant_type,
            is_openid = access_token_is_openid,
            scopes_str = scopes_str,
            issuer = ISSUER,
            lifespan = ACCESS_TOKEN_LIFESPAN,
            jwt_alg = JWT_ALG,
        )
        tokens['access_token'] = access_token

        return TokenResponse.model_validate(tokens)
        
    @staticmethod
    def _build_refresh_token(client_uuid: UUID, user_uuid: UUID | None, length: int, scopes_str: str, lifespan: int) -> str:
        refresh_token = SecurityHandler._generate_random_token(
            length = length,
        )
        with get_db_session() as s:
            refresh_token_obj = RefreshToken(
                token = refresh_token,
                application_uuid=client_uuid,
                user_uuid=user_uuid,
                scope_str=scopes_str,
                expires_in_s=lifespan,
            )
            s.add(refresh_token_obj)
        return refresh_token

    @staticmethod
    def _build_id_token(client_key: str, user: User | None, scopes: list[str], issuer: str, lifespan: int, jwt_alg: str = "RS256") -> str:
        with get_db_session() as session:
            user = session.merge(user)
            idtoken_payload: dict[str, str | int | bool] = {
                'iss': issuer,
                'aud': client_key,
                'sub': user.get_id(),
            }

            # process openid scopes
            if("profile" in scopes or "name" in scopes):
                idtoken_payload['name'] = user.name
            if("email" in scopes):
                idtoken_payload['email'] = user.email
            if("email_verified" in scopes):
                idtoken_payload['email_verified'] = user.email_verified

        # build idtoken
        idtoken = generate_jwt(
            payload = idtoken_payload,
            private_key = key_manager.get_private_key(),
            algorithm = jwt_alg,
            expires_in = lifespan,
        )
        return idtoken

    @staticmethod
    def _build_access_token(audience: str, client_key: str, user_key: str | None, org_key: str | None, grant_type: GrantType, is_openid: str, scopes_str: str, issuer: str, lifespan: int, jwt_alg: str = "RS256") -> str:
        payload = {
            'iss': issuer,
            'client_id': client_key,
        }

        if(user_key is not None):
            payload['sub'] = user_key
            if(org_key is not None):
                payload['org_id'] = org_key

        if is_openid:
            payload['aud'] = [
                audience,
                f"{issuer}oauth2/userinfo" # TODO this is a workaround -- all these URLs should be centrally accessible from some place...
            ]    
        else:
            payload['aud'] = audience
    
        if len(scopes_str) != 0: payload['scope'] = scopes_str
        if grant_type == GrantType.REFRESH_TOKEN: payload['gty'] = grant_type.value

        token = generate_jwt(
            payload = payload,
            private_key = key_manager.get_private_key(),
            algorithm = jwt_alg,
            expires_in = lifespan,
        )
        return token
