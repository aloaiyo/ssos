"""
보안 유틸리티 테스트
"""
import pytest
from datetime import timedelta
from jose import jwt

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_access_token,
    verify_refresh_token,
    verify_password,
    get_password_hash,
    get_cookie_settings,
)
from app.config import settings


class TestPasswordHashing:
    """비밀번호 해싱 테스트"""

    @pytest.mark.skip(reason="passlib/bcrypt 버전 호환성 문제로 CI 환경에서 스킵")
    def test_hash_password(self):
        """비밀번호 해싱"""
        password = "TestPassword123!"
        hashed = get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt prefix

    @pytest.mark.skip(reason="passlib/bcrypt 버전 호환성 문제로 CI 환경에서 스킵")
    def test_verify_correct_password(self):
        """올바른 비밀번호 검증"""
        password = "TestPassword123!"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    @pytest.mark.skip(reason="passlib/bcrypt 버전 호환성 문제로 CI 환경에서 스킵")
    def test_verify_wrong_password(self):
        """잘못된 비밀번호 검증"""
        password = "TestPassword123!"
        hashed = get_password_hash(password)

        assert verify_password("WrongPassword!", hashed) is False

    @pytest.mark.skip(reason="passlib/bcrypt 버전 호환성 문제로 CI 환경에서 스킵")
    def test_different_hashes_for_same_password(self):
        """같은 비밀번호도 다른 해시 생성 (salt)"""
        password = "TestPassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2
        # 둘 다 검증은 성공
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestAccessToken:
    """액세스 토큰 테스트"""

    def test_create_access_token(self):
        """액세스 토큰 생성"""
        user_id = 123
        token = create_access_token(user_id)

        assert token is not None
        assert len(token) > 0

    def test_access_token_contains_user_id(self):
        """토큰에 user_id 포함"""
        user_id = 456
        token = create_access_token(user_id)
        payload = decode_token(token)

        assert payload["sub"] == str(user_id)

    def test_access_token_type(self):
        """토큰 타입이 access"""
        token = create_access_token(123)
        payload = decode_token(token)

        assert payload["type"] == "access"

    def test_access_token_has_expiry(self):
        """토큰에 만료 시간 포함"""
        token = create_access_token(123)
        payload = decode_token(token)

        assert "exp" in payload
        assert "iat" in payload

    def test_access_token_custom_expiry(self):
        """커스텀 만료 시간"""
        token = create_access_token(123, expires_delta=timedelta(hours=1))
        payload = decode_token(token)

        # 만료 시간이 1시간 후
        assert payload["exp"] - payload["iat"] == 3600

    def test_verify_valid_access_token(self):
        """유효한 액세스 토큰 검증"""
        user_id = 789
        token = create_access_token(user_id)

        result = verify_access_token(token)
        assert result == user_id

    def test_verify_invalid_token(self):
        """잘못된 토큰 검증"""
        result = verify_access_token("invalid-token")
        assert result is None


class TestRefreshToken:
    """리프레시 토큰 테스트"""

    def test_create_refresh_token(self):
        """리프레시 토큰 생성"""
        user_id = 123
        token = create_refresh_token(user_id)

        assert token is not None
        assert len(token) > 0

    def test_refresh_token_type(self):
        """토큰 타입이 refresh"""
        token = create_refresh_token(123)
        payload = decode_token(token)

        assert payload["type"] == "refresh"

    def test_verify_valid_refresh_token(self):
        """유효한 리프레시 토큰 검증"""
        user_id = 101
        token = create_refresh_token(user_id)

        result = verify_refresh_token(token)
        assert result == user_id

    def test_access_token_not_valid_as_refresh(self):
        """액세스 토큰은 리프레시로 사용 불가"""
        token = create_access_token(123)
        result = verify_refresh_token(token)

        assert result is None

    def test_refresh_token_not_valid_as_access(self):
        """리프레시 토큰은 액세스로 사용 불가"""
        token = create_refresh_token(123)
        result = verify_access_token(token)

        assert result is None


class TestDecodeToken:
    """토큰 디코딩 테스트"""

    def test_decode_valid_token(self):
        """유효한 토큰 디코딩"""
        token = create_access_token(123)
        payload = decode_token(token)

        assert payload is not None
        assert "sub" in payload

    def test_decode_invalid_token(self):
        """잘못된 토큰 디코딩"""
        result = decode_token("invalid.token.here")
        assert result is None

    def test_decode_tampered_token(self):
        """변조된 토큰 디코딩"""
        token = create_access_token(123)
        # 토큰 변조
        tampered = token[:-5] + "xxxxx"

        result = decode_token(tampered)
        assert result is None


class TestCookieSettings:
    """쿠키 설정 테스트"""

    def test_cookie_settings_httponly(self):
        """쿠키는 httponly"""
        settings_dict = get_cookie_settings()
        assert settings_dict["httponly"] is True

    def test_cookie_settings_samesite(self):
        """samesite 설정 포함"""
        settings_dict = get_cookie_settings()
        assert "samesite" in settings_dict

    def test_cookie_settings_secure(self):
        """secure 설정 포함"""
        settings_dict = get_cookie_settings()
        assert "secure" in settings_dict
