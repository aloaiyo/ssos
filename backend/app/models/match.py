"""
경기 모델
"""
from tortoise import fields
from tortoise.models import Model
from enum import Enum


class MatchType(str, Enum):
    """경기 타입"""
    MENS_DOUBLES = "mens_doubles"
    MIXED_DOUBLES = "mixed_doubles"
    SINGLES = "singles"


class MatchStatus(str, Enum):
    """경기 상태"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Team(str, Enum):
    """팀 구분"""
    A = "A"
    B = "B"


class Match(Model):
    """경기 모델"""

    id = fields.IntField(pk=True)
    session = fields.ForeignKeyField(
        "models.Session",
        related_name="matches",
        on_delete=fields.CASCADE
    )
    match_number = fields.IntField()
    court_number = fields.IntField()
    scheduled_time = fields.TimeField()
    match_type = fields.CharEnumField(MatchType)
    status = fields.CharEnumField(MatchStatus, default=MatchStatus.SCHEDULED)
    actual_start_time = fields.DatetimeField(null=True)
    actual_end_time = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    # 관계
    participants: fields.ReverseRelation["MatchParticipant"]
    result: fields.ReverseRelation["MatchResult"]

    class Meta:
        table = "matches"
        ordering = ["match_number"]

    def __str__(self) -> str:
        return f"Match #{self.match_number} - Court {self.court_number}"


class MatchParticipant(Model):
    """경기 참가자"""

    id = fields.IntField(pk=True)
    match = fields.ForeignKeyField(
        "models.Match",
        related_name="participants",
        on_delete=fields.CASCADE
    )
    club_member = fields.ForeignKeyField(
        "models.ClubMember",
        related_name="match_participations",
        on_delete=fields.CASCADE
    )
    team = fields.CharEnumField(Team)
    position = fields.IntField()  # 1 or 2

    class Meta:
        table = "match_participants"
        unique_together = [("match", "club_member")]
        ordering = ["team", "position"]

    def __str__(self) -> str:
        return f"{self.club_member.user.name} - Team {self.team} (Pos {self.position})"


class MatchResult(Model):
    """경기 결과"""

    id = fields.IntField(pk=True)
    match = fields.OneToOneField(
        "models.Match",
        related_name="result",
        on_delete=fields.CASCADE
    )
    team_a_score = fields.IntField()
    team_b_score = fields.IntField()
    sets_detail = fields.JSONField()  # 세트별 점수 상세
    winner_team = fields.CharEnumField(Team, null=True)
    recorded_by = fields.ForeignKeyField(
        "models.User",
        related_name="recorded_results",
        on_delete=fields.SET_NULL,
        null=True
    )
    recorded_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "match_results"
        ordering = ["-recorded_at"]

    def __str__(self) -> str:
        return f"{self.match} - {self.team_a_score}:{self.team_b_score}"
