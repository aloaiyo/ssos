"""
인증 서비스
"""
from typing import Optional
from app.models.user import User
from app.core.security import verify_password, get_password_hash, create_access_token
from app.schemas.user import UserCreate
from datetime import timedelta
from app.config import settings


async def authenticate_user(email: str, password: str) -> Optional[User]:
    """사용자 인증"""
    user = await User.get_or_none(email=email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


async def create_user(user_data: UserCreate) -> User:
    """사용자 생성"""
    password_hash = get_password_hash(user_data.password)
    user = await User.create(
        email=user_data.email,
        name=user_data.name,
        password_hash=password_hash
    )
    return user


def create_user_token(user_id: int) -> str:
    """사용자 토큰 생성"""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user_id)}, expires_delta=access_token_expires
    )
    return access_token
