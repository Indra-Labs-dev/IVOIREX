from pydantic import BaseModel, EmailStr, Field
class RegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(pattern=r"^[A-Za-z0-9_]{3,32}$")
    password: str = Field(min_length=12, max_length=72)
class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)
class UserResponse(BaseModel):
    id: str
    email: EmailStr
    username: str
    role: str
class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
class AuthResponse(TokenPair):
    user: UserResponse
class RefreshRequest(BaseModel):
    refresh_token: str
