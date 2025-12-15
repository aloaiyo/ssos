"""
동호회 회원 모델
"""
from tortoise import fields
from app.models.base import BaseModel
from enum import Enum


class MemberRole(str, Enum):
    """회원 역할"""
    MANAGER = "manager"  # 클럽 관리자
    MEMBER = "member"    # 일반 회원


class MemberStatus(str, Enum):
    """회원 상태"""
    PENDING = "pending"    # 가입 대기
    ACTIVE = "active"      # 활성 (승인됨)
    INACTIVE = "inactive"  # 비활성


class Gender(str, Enum):
    """성별"""
    MALE = "male"
    FEMALE = "female"


class ClubMember(BaseModel):
    """동호회 회원 모델"""

    id = fields.IntField(pk=True)
    club = fields.ForeignKeyField(
        "models.Club",
        related_name="members",
        on_delete=fields.CASCADE
    )
    user = fields.ForeignKeyField(
        "models.User",
        related_name="club_memberships",
        on_delete=fields.CASCADE
    )
    role = fields.CharEnumField(MemberRole, default=MemberRole.MEMBER)
    status = fields.CharEnumField(MemberStatus, default=MemberStatus.PENDING)
    nickname = fields.CharField(max_length=100, null=True)  # 클럽 내 닉네임
    gender = fields.CharEnumField(Gender)

    # 통계
    total_games = fields.IntField(default=0)
    wins = fields.IntField(default=0)
    losses = fields.IntField(default=0)
    draws = fields.IntField(default=0)

    # 관계
    session_participations: fields.ReverseRelation["SessionParticipant"]
    match_participations: fields.ReverseRelation["MatchParticipant"]
    rankings: fields.ReverseRelation["Ranking"]

    class Meta:
        table = "club_members"
        unique_together = [("club", "user")]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.nickname or self.user.name} @ {self.club.name}"

    @property
    def win_rate(self) -> float:
        """승률 계산"""
        if self.total_games == 0:
            return 0.0
        return round(self.wins / self.total_games * 100, 1)

    @property
    def is_manager(self) -> bool:
        """관리자 여부"""
        return self.role == MemberRole.MANAGER
