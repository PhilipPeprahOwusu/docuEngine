"""Authentication Schemas"""
from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    """Token schema"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data schema"""
    user_id: Optional[int] = None
    username: Optional[str] = None


class TokenPayload(BaseModel):
    """Token payload schema"""
    sub: Optional[str] = None  # Changed to str to support UUID
    exp: Optional[int] = None
