import jwt
from datetime import datetime, timedelta, timezone

def generate_jwt(payload, private_key, algorithm="RS256", expires_in=3600):
    payload["iat"] = datetime.now(tz=timezone.utc)
    payload["exp"] = datetime.now(tz=timezone.utc) + timedelta(seconds=expires_in)
    return jwt.encode(payload, private_key, algorithm=algorithm)