from datetime import timedelta
import jwt
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher
from app.api.deps import current_user
from app.api.rate_limit import rate_limit
from app.core.database import get_db
from app.core.settings import settings
from app.models.domain import Profile, User
from app.schemas.auth import AuthResponse, LoginRequest, RefreshRequest, RegisterRequest, TokenPair, UserResponse
from app.security.tokens import decode_claims, issue_token
router = APIRouter(prefix="/auth", tags=["auth"])
hasher = PasswordHash((Argon2Hasher(), BcryptHasher()))
def user_response(user: User) -> UserResponse:
    return UserResponse(id=user.id, email=user.email, username=user.username, role=user.role)
def token_pair(user: User) -> TokenPair:
    return TokenPair(access_token=issue_token(user.id, "access", timedelta(minutes=settings.jwt_access_minutes), user.token_version), refresh_token=issue_token(user.id, "refresh", timedelta(days=settings.jwt_refresh_days), user.token_version))
@router.post("/register", status_code=201, response_model=AuthResponse, dependencies=[Depends(rate_limit("register", 5, 60))])
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    email = str(body.email).lower()
    if db.scalar(select(User).where(or_(User.email == email, User.username == body.username))):
        raise HTTPException(status_code=409, detail="Email or username already used")
    user = User(email=email, username=body.username, password_hash=hasher.hash(body.password))
    db.add(user)
    try:
        db.flush()
        db.add(Profile(user_id=user.id, display_name=user.username, city=user.city, bio=user.bio, skills=[], interests=[]))
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email or username already used") from exc
    db.refresh(user)
    return AuthResponse(**token_pair(user).model_dump(), user=user_response(user))
@router.post("/login", response_model=AuthResponse, dependencies=[Depends(rate_limit("login", 10, 60))])
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == str(body.email).lower()))
    try:
        verified, updated_hash = hasher.verify_and_update(body.password, user.password_hash) if user else (False, None)
    except UnknownHashError:
        verified, updated_hash = False, None
    if user is None or not verified:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if updated_hash is not None:
        user.password_hash = updated_hash
        db.commit()
    return AuthResponse(**token_pair(user).model_dump(), user=user_response(user))
@router.post("/refresh", response_model=TokenPair, dependencies=[Depends(rate_limit("refresh", 20, 60))])
def refresh(body: RefreshRequest, db: Session = Depends(get_db)):
    try:
        claims = decode_claims(body.refresh_token, "refresh")
        user_id = str(claims["sub"])
    except (jwt.PyJWTError, KeyError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token") from exc
    user = db.get(User, user_id)
    if user is None or claims.get("ver") != user.token_version:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    return token_pair(user)
@router.post("/logout", status_code=204)
def logout(user: User = Depends(current_user), db: Session = Depends(get_db)):
    # Incrementing the account token version invalidates every outstanding access and refresh token.
    user.token_version += 1
    db.commit()
    return Response(status_code=204)
@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(current_user)):
    return user_response(user)
