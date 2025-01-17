from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.config import load_settings
from app.security.key_management import KeyManager

import logging

logger = logging.getLogger(__name__)

settings = load_settings()

router = APIRouter()

@router.get("/.well_known/openid-configuration")
async def oidc_discovery(request: Request):
    """
    OIDC Discovery Endpoint
    """
    discovery_document = {
        "issuer": settings.app_host_public_url,
        "authorization_endpoint": str(request.url_for("authorize")),
        "token_endpoint": str(request.url_for("get_token")),
        "userinfo_endpoint": str(request.url_for("get_userinfo")),
        "jwks_uri": str(request.url_for("list_jwks")),
        "response_types_supported": [
            "code",
        ], # dynamically fetch.. from where?
        "subject_types_supported": [
            "public"
        ],
        "id_token_signing_alg_values_supported": ["RS256"],
        "scopes_supported": [
            "openid",
            "profile",
            "email",
            "offline_access",
            # todo add resource-specific namespaced scopes here
        ],
        "token_endpoint_auth_methods_supported": ["client_secret_post"],
        "claims_supported": [
            "sub",
            "name",
            "email",
            "email_verified",
        ]
    }

    return JSONResponse(content=discovery_document)
    
@router.get("/oauth2/certs")
async def list_jwks():
    k = KeyManager()
    jwk_document = {"keys": [{
        "kty": "RSA",
        "use": "sig",
        "kid": k.get_kid(),
        **k.get_public_key_info(),
        "alg": "RS256",
    }]}
    return jwk_document