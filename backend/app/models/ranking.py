"""
랭킹 모델
"""
from tortoise import fields
from app.models.base import BaseModel


class Ranking(BaseModel):
    """랭킹 모델"""

    id = fields.IntField(pk=True)
    club = fields.ForeignKeyField(
        "models.Club",
        related_name="rankings",
        on_delete=fields.CASCADE
    )
    club_member = fields.ForeignKeyField(
        "models.ClubMember",
        related_name="rankings",
        on_delete=fields.CASCADE
    )
    total_matches = fields.IntField(default=0)
    wins = fields.IntField(default=0)
    draws = fields.IntField(default=0)
    losses = fields.IntField(default=0)
    points = fields.IntField(default=0)
    last_updated = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "rankings"
        unique_together = [("club", "club_member")]
        ordering = ["-points", "-wins"]

    def __str__(self) -> str:
        return f"{self.club_member.user.name} - {self.points}pts"

    @property
    def win_rate(self) -> float:
        """승률 계산"""
        if self.total_matches == 0:
            return 0.0
        return (self.wins / self.total_matches) * 100
