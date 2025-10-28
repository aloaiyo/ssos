"""
동호회 회원 모델
"""
from tortoise import fields
from tortoise.models import Model
from enum import Enum


class MemberRole(str, Enum):
    """회원 역할"""
    ADMIN = "admin"
    MEMBER = "member"


class Gender(str, Enum):
    """성별"""
    MALE = "male"
    FEMALE = "female"


class PreferredType(str, Enum):
    """선호 경기 타입"""
    MENS_DOUBLES = "mens_doubles"
    MIXED_DOUBLES = "mixed_doubles"
    SINGLES = "singles"


class ClubMember(Model):
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
    gender = fields.CharEnumField(Gender)
    preferred_type = fields.CharEnumField(PreferredType)
    joined_at = fields.DatetimeField(auto_now_add=True)

    # 관계
    session_participations: fields.ReverseRelation["SessionParticipant"]
    match_participations: fields.ReverseRelation["MatchParticipant"]
    rankings: fields.ReverseRelation["Ranking"]

    class Meta:
        table = "club_members"
        unique_together = [("club", "user")]
        ordering = ["-joined_at"]

    def __str__(self) -> str:
        return f"{self.user.name} @ {self.club.name}"
