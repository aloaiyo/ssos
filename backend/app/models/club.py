"""
동호회 모델
"""
from tortoise import fields
from tortoise.models import Model


class Club(Model):
    """동호회 모델"""

    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=200)
    description = fields.TextField(null=True)
    created_by = fields.ForeignKeyField(
        "models.User",
        related_name="created_clubs",
        on_delete=fields.CASCADE
    )
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    # 관계
    members: fields.ReverseRelation["ClubMember"]
    events: fields.ReverseRelation["Event"]
    session_configs: fields.ReverseRelation["SessionConfig"]
    rankings: fields.ReverseRelation["Ranking"]

    class Meta:
        table = "clubs"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name
