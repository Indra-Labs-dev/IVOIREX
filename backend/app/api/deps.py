import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.domain import User
from app.security.tokens import decode_claims
bearer = HTTPBearer(auto_error=False)
def _resolve_user(credentials: HTTPAuthorizationCredentials | None, db: Session) -> User | None:
    if credentials is None:
        return None
    try:
        claims = decode_claims(credentials.credentials, "access")
        user_id = str(claims["sub"])
    except (jwt.PyJWTError, KeyError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired access token") from exc
    user = db.get(User, user_id)
    if user is None or claims.get("ver") != user.token_version:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")
    return user


def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> User:
    user = _resolve_user(credentials, db)
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required", headers={"WWW-Authenticate": "Bearer"})
    return user


def optional_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> User | None:
    return _resolve_user(credentials, db)
