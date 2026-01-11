"""
시즌 모델
"""
from tortoise import fields
from app.models.base import BaseModel
from enum import Enum


class SeasonStatus(str, Enum):
    """시즌 상태"""
    UPCOMING = "upcoming"      # 예정
    ACTIVE = "active"          # 진행 중
    COMPLETED = "completed"    # 완료


class Season(BaseModel):
    """시즌 모델 - 순위와 결과를 집계하는 기간 단위"""

    id = fields.IntField(pk=True)
    club = fields.ForeignKeyField(
        "models.Club",
        related_name="seasons",
        on_delete=fields.CASCADE
    )
    name = fields.CharField(max_length=100)  # 예: "2024 상반기", "2024 Winter League"
    description = fields.TextField(null=True)
    start_date = fields.DateField()
    end_date = fields.DateField()
    status = fields.CharEnumField(SeasonStatus, default=SeasonStatus.UPCOMING)
    created_at = fields.DatetimeField(auto_now_add=True)

    # 관계
    sessions: fields.ReverseRelation["Session"]
    rankings: fields.ReverseRelation["SeasonRanking"]

    class Meta:
        table = "seasons"
        ordering = ["-start_date"]

    def __str__(self) -> str:
        return f"{self.name} ({self.start_date} ~ {self.end_date})"


class SeasonRanking(BaseModel):
    """시즌별 랭킹"""

    id = fields.IntField(pk=True)
    season = fields.ForeignKeyField(
        "models.Season",
        related_name="rankings",
        on_delete=fields.CASCADE
    )
    club_member = fields.ForeignKeyField(
        "models.ClubMember",
        related_name="season_rankings",
        on_delete=fields.CASCADE
    )
    total_matches = fields.IntField(default=0)
    wins = fields.IntField(default=0)
    draws = fields.IntField(default=0)
    losses = fields.IntField(default=0)
    points = fields.IntField(default=0)
    rank = fields.IntField(null=True)  # 순위
    last_updated = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "season_rankings"
        unique_together = [("season", "club_member")]
        ordering = ["-points", "-wins", "losses"]

    def __str__(self) -> str:
        return f"{self.club_member} - Season {self.season.name}: {self.points}pts"

    @property
    def win_rate(self) -> float:
        """승률 계산"""
        if self.total_matches == 0:
            return 0.0
        return (self.wins / self.total_matches) * 100
