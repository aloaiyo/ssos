"""
모델 테스트
"""
import pytest
from datetime import date, timedelta

from app.models.user import User, UserRole, SubscriptionTier
from app.models.club import Club
from app.models.member import ClubMember, MemberRole, MemberStatus, Gender
from app.models.season import Season, SeasonStatus
from app.models.match import MatchType, MatchStatus, Team


class TestUserModel:
    """User 모델 테스트"""

    @pytest.mark.asyncio
    async def test_create_user(self, db):
        """사용자 생성"""
        user = await User.create(
            email="newuser@test.com",
            cognito_sub="new-sub-123",
            name="새사용자",
            role=UserRole.USER,
        )

        assert user.id is not None
        assert user.email == "newuser@test.com"
        assert user.name == "새사용자"

    @pytest.mark.asyncio
    async def test_user_default_values(self, db):
        """기본값 확인"""
        user = await User.create(
            email="default@test.com",
            cognito_sub="default-sub",
            name="기본값테스트",
        )

        assert user.role == UserRole.USER
        assert user.subscription_tier == SubscriptionTier.FREE
        assert user.is_deleted is False

    @pytest.mark.asyncio
    async def test_is_super_admin_property(self, test_user, test_admin):
        """is_super_admin 프로퍼티"""
        assert test_user.is_super_admin is False
        assert test_admin.is_super_admin is True

    @pytest.mark.asyncio
    async def test_is_premium_without_subscription(self, test_user):
        """구독 없는 사용자는 프리미엄 아님"""
        assert test_user.is_premium is False

    @pytest.mark.asyncio
    async def test_is_premium_with_expired_subscription(self, db):
        """만료된 구독은 프리미엄 아님"""
        from app.core.timezone import utc_now

        user = await User.create(
            email="expired@test.com",
            cognito_sub="expired-sub",
            name="만료된구독",
            subscription_tier=SubscriptionTier.PREMIUM,
            subscription_expires_at=utc_now() - timedelta(days=1),
        )

        assert user.is_premium is False

    @pytest.mark.asyncio
    async def test_is_premium_with_valid_subscription(self, db):
        """유효한 구독은 프리미엄"""
        from app.core.timezone import utc_now

        user = await User.create(
            email="premium@test.com",
            cognito_sub="premium-sub",
            name="프리미엄사용자",
            subscription_tier=SubscriptionTier.PREMIUM,
            subscription_expires_at=utc_now() + timedelta(days=30),
        )

        assert user.is_premium is True

    @pytest.mark.asyncio
    async def test_max_manager_clubs(self, test_user, test_admin):
        """관리 가능 클럽 수"""
        assert test_user.max_manager_clubs == 1  # FREE
        assert test_admin.max_manager_clubs == 999  # SUPER_ADMIN


class TestClubModel:
    """Club 모델 테스트"""

    @pytest.mark.asyncio
    async def test_create_club(self, db, test_user):
        """동호회 생성"""
        club = await Club.create(
            name="새 동호회",
            description="설명",
            created_by=test_user,
        )

        assert club.id is not None
        assert club.name == "새 동호회"
        assert club.created_by_id == test_user.id

    @pytest.mark.asyncio
    async def test_club_default_values(self, db, test_user):
        """기본값 확인"""
        club = await Club.create(
            name="기본값 테스트",
            created_by=test_user,
        )

        assert club.is_join_allowed is True
        assert club.requires_approval is False
        assert club.is_deleted is False

    @pytest.mark.asyncio
    async def test_club_string_representation(self, test_club):
        """__str__ 메서드"""
        assert str(test_club) == "테스트 동호회"


class TestClubMemberModel:
    """ClubMember 모델 테스트"""

    @pytest.mark.asyncio
    async def test_create_member(self, db, test_club, test_user):
        """회원 생성"""
        member = await ClubMember.create(
            club=test_club,
            user=test_user,
            role=MemberRole.MEMBER,
            status=MemberStatus.ACTIVE,
            gender=Gender.MALE,
        )

        assert member.id is not None
        assert member.club_id == test_club.id
        assert member.user_id == test_user.id

    @pytest.mark.asyncio
    async def test_member_roles(self, db, test_club, test_user):
        """회원 역할"""
        # 매니저
        manager = await ClubMember.create(
            club=test_club,
            user=test_user,
            role=MemberRole.MANAGER,
            status=MemberStatus.ACTIVE,
            gender=Gender.MALE,
        )
        assert manager.role == MemberRole.MANAGER

    @pytest.mark.asyncio
    async def test_member_statuses(self):
        """회원 상태 enum"""
        assert MemberStatus.ACTIVE.value == "active"
        assert MemberStatus.PENDING.value == "pending"
        assert MemberStatus.LEFT.value == "left"
        assert MemberStatus.BANNED.value == "banned"


class TestSeasonModel:
    """Season 모델 테스트"""

    @pytest.mark.asyncio
    async def test_create_season(self, db, test_club):
        """시즌 생성"""
        today = date.today()
        season = await Season.create(
            club=test_club,
            name="테스트 시즌",
            start_date=today,
            end_date=today + timedelta(days=90),
            status=SeasonStatus.ACTIVE,
        )

        assert season.id is not None
        assert season.name == "테스트 시즌"
        assert season.club_id == test_club.id

    @pytest.mark.asyncio
    async def test_season_statuses(self):
        """시즌 상태 enum"""
        assert SeasonStatus.UPCOMING.value == "upcoming"
        assert SeasonStatus.ACTIVE.value == "active"
        assert SeasonStatus.COMPLETED.value == "completed"


class TestMatchEnums:
    """Match 관련 enum 테스트"""

    def test_match_types(self):
        """경기 유형"""
        assert MatchType.SINGLES.value == "singles"
        assert MatchType.MENS_DOUBLES.value == "mens_doubles"
        assert MatchType.WOMENS_DOUBLES.value == "womens_doubles"
        assert MatchType.MIXED_DOUBLES.value == "mixed_doubles"

    def test_match_statuses(self):
        """경기 상태"""
        assert MatchStatus.SCHEDULED.value == "scheduled"
        assert MatchStatus.IN_PROGRESS.value == "in_progress"
        assert MatchStatus.COMPLETED.value == "completed"

    def test_teams(self):
        """팀"""
        assert Team.A.value == "A"
        assert Team.B.value == "B"
