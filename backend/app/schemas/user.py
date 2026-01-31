"""
사용자 스키마
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from pydantic import ConfigDict
from datetime import date
from typing import Optional
import re
from app.core.timezone import KSTDatetime, OptionalKSTDatetime


class UserBase(BaseModel):
    """사용자 기본 스키마"""
    email: EmailStr
    name: str


class SignUpRequest(BaseModel):
    """회원가입 요청 스키마"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=1, max_length=100)

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """비밀번호 검증: 8자 이상, 숫자 1개, 기호 1개, 대문자 1개"""
        if len(v) < 8:
            raise ValueError('비밀번호는 8자 이상이어야 합니다')
        if not re.search(r'[0-9]', v):
            raise ValueError('비밀번호에 숫자가 1개 이상 포함되어야 합니다')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('비밀번호에 특수문자가 1개 이상 포함되어야 합니다')
        if not re.search(r'[A-Z]', v):
            raise ValueError('비밀번호에 대문자가 1개 이상 포함되어야 합니다')
        return v


class VerifyEmailRequest(BaseModel):
    """이메일 인증 요청 스키마"""
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)


class EmailLoginRequest(BaseModel):
    """이메일 로그인 요청 스키마"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """사용자 수정 스키마"""
    name: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[date] = None


class UserResponse(BaseModel):
    """사용자 응답 스키마"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: Optional[str] = None
    name: str
    role: str
    subscription_tier: str
    is_premium: bool
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    created_at: KSTDatetime


class UserProfileResponse(BaseModel):
    """사용자 프로필 응답 (대시보드용)"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: Optional[str] = None
    name: str
    role: str
    subscription_tier: str
    is_premium: bool
    max_manager_clubs: int
    gender: Optional[str] = None
    birth_date: Optional[date] = None


class Token(BaseModel):
    """토큰 스키마 (쿠키 설정 확인용)"""
    message: str = "로그인 성공"
    user: UserResponse


class TokenData(BaseModel):
    """토큰 데이터 스키마"""
    user_id: Optional[int] = None
    token_type: Optional[str] = None  # "access" or "refresh"


class CognitoCallbackRequest(BaseModel):
    """Cognito Hosted UI 콜백 요청 스키마"""
    code: str


class RefreshTokenRequest(BaseModel):
    """토큰 갱신 요청 스키마 (쿠키에서 자동으로 읽음)"""
    pass


class SubscriptionUpgradeRequest(BaseModel):
    """구독 업그레이드 요청"""
    tier: str = Field(..., pattern="^(premium)$")
    months: int = Field(..., ge=1, le=12)


class SubscriptionResponse(BaseModel):
    """구독 상태 응답"""
    model_config = ConfigDict(from_attributes=True)

    subscription_tier: str
    is_premium: bool
    subscription_expires_at: OptionalKSTDatetime = None
    max_manager_clubs: int
