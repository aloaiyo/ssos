"""
Pydantic 스키마 테스트
"""
import pytest
from datetime import datetime, date, time, timezone, timedelta
from pydantic import ValidationError

from app.core.timezone import KST
from app.schemas.user import (
    SignUpRequest,
    UserUpdate,
    UserResponse,
)
from app.schemas.club import ClubCreate, ClubUpdate, ClubResponse
from app.schemas.season import SeasonCreate, SeasonResponse
from app.schemas.event import SessionCreate


class TestSignUpRequestSchema:
    """회원가입 스키마 테스트"""

    def test_valid_signup(self):
        """유효한 회원가입"""
        data = SignUpRequest(
            email="test@example.com",
            password="Test1234!",
            name="테스트",
        )
        assert data.email == "test@example.com"
        assert data.name == "테스트"

    def test_invalid_email(self):
        """잘못된 이메일"""
        with pytest.raises(ValidationError):
            SignUpRequest(
                email="invalid-email",
                password="Test1234!",
                name="테스트",
            )

    def test_password_too_short(self):
        """비밀번호 너무 짧음"""
        with pytest.raises(ValidationError):
            SignUpRequest(
                email="test@example.com",
                password="Test1!",  # 6자
                name="테스트",
            )

    def test_password_no_number(self):
        """비밀번호 숫자 없음"""
        with pytest.raises(ValidationError) as exc_info:
            SignUpRequest(
                email="test@example.com",
                password="TestTest!",
                name="테스트",
            )
        assert "숫자" in str(exc_info.value)

    def test_password_no_special_char(self):
        """비밀번호 특수문자 없음"""
        with pytest.raises(ValidationError) as exc_info:
            SignUpRequest(
                email="test@example.com",
                password="Test1234",
                name="테스트",
            )
        assert "특수문자" in str(exc_info.value)

    def test_password_no_uppercase(self):
        """비밀번호 대문자 없음"""
        with pytest.raises(ValidationError) as exc_info:
            SignUpRequest(
                email="test@example.com",
                password="test1234!",
                name="테스트",
            )
        assert "대문자" in str(exc_info.value)


class TestUserUpdateSchema:
    """사용자 수정 스키마 테스트"""

    def test_partial_update(self):
        """부분 업데이트"""
        data = UserUpdate(name="새이름")
        assert data.name == "새이름"
        assert data.gender is None

    def test_update_gender(self):
        """성별 업데이트"""
        data = UserUpdate(gender="female")
        assert data.gender == "female"

    def test_update_birth_date(self):
        """생년월일 업데이트"""
        data = UserUpdate(birth_date=date(1990, 1, 15))
        assert data.birth_date == date(1990, 1, 15)


class TestClubCreateSchema:
    """동호회 생성 스키마 테스트"""

    def test_minimal_club(self):
        """최소 정보로 생성"""
        data = ClubCreate(name="테스트 동호회")
        assert data.name == "테스트 동호회"
        assert data.is_join_allowed is True

    def test_full_club(self):
        """전체 정보로 생성"""
        data = ClubCreate(
            name="전체 동호회",
            description="설명입니다",
            default_num_courts=4,
            default_match_duration=30,
            location="서울시",
            is_join_allowed=True,
            requires_approval=True,
        )
        assert data.default_num_courts == 4
        assert data.requires_approval is True


class TestSeasonCreateSchema:
    """시즌 생성 스키마 테스트"""

    def test_create_season(self):
        """시즌 생성"""
        today = date.today()
        data = SeasonCreate(
            name="2026 시즌",
            start_date=today,
            end_date=today + timedelta(days=180),
        )
        assert data.name == "2026 시즌"

    def test_season_with_description(self):
        """설명 포함 시즌"""
        today = date.today()
        data = SeasonCreate(
            name="시즌",
            description="상반기 시즌입니다",
            start_date=today,
            end_date=today + timedelta(days=90),
        )
        assert data.description == "상반기 시즌입니다"


class TestSessionCreateSchema:
    """세션 생성 스키마 테스트"""

    def test_create_session(self):
        """세션 생성"""
        data = SessionCreate(
            date=date.today(),
            start_time=time(9, 0),
            end_time=time(12, 0),
            num_courts=4,
            match_duration_minutes=30,
        )
        assert data.num_courts == 4
        assert data.match_duration_minutes == 30

    def test_session_with_location(self):
        """장소 포함 세션"""
        data = SessionCreate(
            date=date.today(),
            start_time=time(14, 0),
            end_time=time(17, 0),
            num_courts=2,
            match_duration_minutes=25,
            location="올림픽 테니스장",
        )
        assert data.location == "올림픽 테니스장"


class TestKSTDatetimeSerialization:
    """KSTDatetime 직렬화 테스트"""

    def test_response_datetime_is_kst(self):
        """응답 datetime은 KST로 직렬화"""
        # UTC 시간으로 데이터 생성
        utc_time = datetime(2026, 1, 31, 9, 0, 0, tzinfo=timezone.utc)

        # 모의 응답 데이터
        response_data = {
            "id": 1,
            "name": "테스트",
            "description": None,
            "start_date": date(2026, 1, 1),
            "end_date": date(2026, 6, 30),
            "club_id": 1,
            "status": "active",
            "created_at": utc_time,
        }

        response = SeasonResponse(**response_data)

        # JSON 직렬화 시 KST로 변환
        json_data = response.model_dump(mode="json")
        created_at_str = json_data["created_at"]

        # KST 시간대 확인 (+09:00)
        assert "+09:00" in created_at_str
        # 시간이 18시로 변환 (9 + 9 = 18)
        assert "18:00:00" in created_at_str
