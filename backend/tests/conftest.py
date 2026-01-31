"""
pytest 설정 및 공통 fixture
"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import MagicMock, AsyncMock

from httpx import AsyncClient, ASGITransport
from tortoise import Tortoise

from app.main import app
from app.models.user import User, UserRole, SubscriptionTier
from app.models.club import Club
from app.models.member import ClubMember, MemberRole, MemberStatus, Gender
from app.models.season import Season, SeasonStatus
from app.models.event import Session, SessionStatus, SessionType


# pytest-asyncio 설정
@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """세션 스코프 이벤트 루프"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db() -> AsyncGenerator[None, None]:
    """
    테스트용 인메모리 SQLite 데이터베이스
    각 테스트 함수마다 새로운 DB 생성
    """
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={"models": ["app.models"]},
    )
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


@pytest.fixture
async def client(db) -> AsyncGenerator[AsyncClient, None]:
    """비동기 HTTP 테스트 클라이언트"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_user(db) -> User:
    """테스트용 일반 사용자"""
    user = await User.create(
        email="test@example.com",
        cognito_sub="test-cognito-sub-123",
        name="테스트유저",
        role=UserRole.USER,
        subscription_tier=SubscriptionTier.FREE,
        gender="male",
    )
    return user


@pytest.fixture
async def test_admin(db) -> User:
    """테스트용 슈퍼 관리자"""
    admin = await User.create(
        email="admin@example.com",
        cognito_sub="admin-cognito-sub-456",
        name="관리자",
        role=UserRole.SUPER_ADMIN,
        subscription_tier=SubscriptionTier.PREMIUM,
        gender="male",
    )
    return admin


@pytest.fixture
async def test_club(db, test_user) -> Club:
    """테스트용 동호회"""
    club = await Club.create(
        name="테스트 동호회",
        description="테스트용 동호회입니다",
        created_by=test_user,
        default_num_courts=4,
        default_match_duration=30,
        location="서울시 강남구",
    )
    return club


@pytest.fixture
async def test_member(db, test_club, test_user) -> ClubMember:
    """테스트용 동호회 회원 (매니저)"""
    member = await ClubMember.create(
        club=test_club,
        user=test_user,
        role=MemberRole.MANAGER,
        status=MemberStatus.ACTIVE,
        gender=Gender.MALE,
    )
    return member


@pytest.fixture
async def test_season(db, test_club) -> Season:
    """테스트용 시즌"""
    from datetime import date, timedelta

    today = date.today()
    season = await Season.create(
        club=test_club,
        name="2026년 상반기",
        description="테스트 시즌",
        start_date=today,
        end_date=today + timedelta(days=180),
        status=SeasonStatus.ACTIVE,
    )
    return season


@pytest.fixture
def mock_current_user(test_user):
    """현재 사용자 의존성 모킹"""
    from app.core import dependencies

    original = dependencies.get_current_active_user

    async def mock_get_user():
        return test_user

    dependencies.get_current_active_user = mock_get_user
    yield test_user
    dependencies.get_current_active_user = original
