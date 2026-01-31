"""
보안 유틸리티 (JWT, 쿠키)
"""
from datetime import timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings
from app.core.timezone import utc_now

# 비밀번호 해싱 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """비밀번호 해싱"""
    return pwd_context.hash(password)


def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """JWT 액세스 토큰 생성"""
    now = utc_now()
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)

    to_encode = {
        "sub": str(user_id),
        "type": "access",
        "exp": expire,
        "iat": now
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """JWT 리프레시 토큰 생성"""
    now = utc_now()
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expire,
        "iat": now
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """JWT 토큰 디코딩"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_access_token(token: str) -> Optional[int]:
    """액세스 토큰 검증 및 user_id 반환"""
    payload = decode_token(token)
    if payload is None:
        return None
    if payload.get("type") != "access":
        return None
    try:
        user_id = int(payload.get("sub"))
        return user_id
    except (ValueError, TypeError):
        return None


def verify_refresh_token(token: str) -> Optional[int]:
    """리프레시 토큰 검증 및 user_id 반환"""
    payload = decode_token(token)
    if payload is None:
        return None
    if payload.get("type") != "refresh":
        return None
    try:
        user_id = int(payload.get("sub"))
        return user_id
    except (ValueError, TypeError):
        return None


# 쿠키 설정 헬퍼
def get_cookie_settings() -> dict:
    """HTTP-only 쿠키 설정 반환"""
    return {
        "httponly": True,
        "secure": settings.COOKIE_SECURE,
        "samesite": settings.COOKIE_SAMESITE,
    }


def get_access_token_cookie_settings() -> dict:
    """액세스 토큰 쿠키 설정"""
    base = get_cookie_settings()
    base["max_age"] = settings.ACCESS_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    return base


def get_refresh_token_cookie_settings() -> dict:
    """리프레시 토큰 쿠키 설정"""
    base = get_cookie_settings()
    base["max_age"] = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    return base
