from datetime import datetime, timedelta, timezone
import jwt
from app.core.settings import settings
ALGORITHM = "HS256"
def issue_token(subject: str, token_type: str, lifetime: timedelta, token_version: int = 0) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": subject, "type": token_type, "ver": token_version, "iat": now, "exp": now + lifetime}
    return jwt.encode(payload, settings.jwt_secret.get_secret_value(), algorithm=ALGORITHM)
def decode_claims(token: str, expected_type: str) -> dict:
    payload = jwt.decode(token, settings.jwt_secret.get_secret_value(), algorithms=[ALGORITHM])
    if payload.get("type") != expected_type:
        raise jwt.InvalidTokenError("Unexpected token type")
    return payload
def decode_token(token: str, expected_type: str) -> str:
    return str(decode_claims(token, expected_type)["sub"])
