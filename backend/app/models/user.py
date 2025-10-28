"""
사용자 모델
"""
from tortoise import fields
from tortoise.models import Model


class User(Model):
    """전역 사용자 모델"""

    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255, unique=True, index=True)
    password_hash = fields.CharField(max_length=255)
    name = fields.CharField(max_length=100)
    is_super_admin = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    # 관계
    created_clubs: fields.ReverseRelation["Club"]
    club_memberships: fields.ReverseRelation["ClubMember"]

    class Meta:
        table = "users"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} ({self.email})"
