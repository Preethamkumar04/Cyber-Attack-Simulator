from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)
    tenant_name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    tenant_slug: Optional[str] = Field(default=None, min_length=2, max_length=50)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    role: str
    tenant_id: int
    tenant_name: str
    tenant_slug: str

    class Config:
        from_attributes = True
