"""
사용자 스키마
"""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """사용자 기본 스키마"""
    email: EmailStr
    name: str


class UserCreate(UserBase):
    """사용자 생성 스키마"""
    password: str


class UserUpdate(BaseModel):
    """사용자 수정 스키마"""
    name: Optional[str] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    """사용자 응답 스키마"""
    id: int
    is_super_admin: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """토큰 스키마"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """토큰 데이터 스키마"""
    user_id: Optional[int] = None
