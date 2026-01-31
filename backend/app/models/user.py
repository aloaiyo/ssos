"""
사용자 모델
"""
from tortoise import fields
from app.models.base import BaseModel
from enum import Enum


class UserRole(str, Enum):
    """사용자 역할"""
    USER = "user"              # 일반 사용자
    SUPER_ADMIN = "super_admin"  # 슈퍼 관리자


class SubscriptionTier(str, Enum):
    """구독 등급"""
    FREE = "free"       # 무료 (manager 1개)
    PREMIUM = "premium"  # 유료 (manager 10개)


class User(BaseModel):
    """전역 사용자 모델"""

    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255, unique=True, index=True, null=True)
    cognito_sub = fields.CharField(max_length=255, unique=True, index=True)
    password_hash = fields.CharField(max_length=255, null=True)  # Cognito 사용 시 사용 안함
    name = fields.CharField(max_length=100)

    # 역할 및 구독
    role = fields.CharEnumField(UserRole, default=UserRole.USER)
    subscription_tier = fields.CharEnumField(SubscriptionTier, default=SubscriptionTier.FREE)
    subscription_expires_at = fields.DatetimeField(null=True)

    # 프로필 정보
    gender = fields.CharField(max_length=10, null=True)  # male, female
    birth_date = fields.DateField(null=True)

    # 관계
    created_clubs: fields.ReverseRelation["Club"]
    club_memberships: fields.ReverseRelation["ClubMember"]
    favorite_clubs: fields.ReverseRelation["UserFavoriteClub"]

    class Meta:
        table = "users"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} ({self.email})"

    @property
    def is_super_admin(self) -> bool:
        """슈퍼 관리자 여부"""
        return self.role == UserRole.SUPER_ADMIN

    @property
    def is_premium(self) -> bool:
        """프리미엄 구독 여부"""
        if self.subscription_tier != SubscriptionTier.PREMIUM:
            return False
        if self.subscription_expires_at is None:
            return False
        from app.core.timezone import utc_now
        return self.subscription_expires_at > utc_now()

    @property
    def max_manager_clubs(self) -> int:
        """관리 가능한 최대 클럽 수"""
        if self.is_super_admin:
            return 999
        return 10 if self.is_premium else 1


class UserFavoriteClub(BaseModel):
    """사용자 즐겨찾기 클럽"""

    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField(
        "models.User",
        related_name="favorite_clubs",
        on_delete=fields.CASCADE
    )
    club = fields.ForeignKeyField(
        "models.Club",
        related_name="favorited_by",
        on_delete=fields.CASCADE
    )
    order = fields.IntField(default=0)  # 정렬 순서

    class Meta:
        table = "user_favorite_clubs"
        unique_together = [("user", "club")]
        ordering = ["order", "-created_at"]
