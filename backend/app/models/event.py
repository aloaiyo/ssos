"""
일정 및 세션 모델
"""
from tortoise import fields
from tortoise.models import Model
from enum import Enum


class EventType(str, Enum):
    """일정 타입"""
    REGULAR = "regular"
    SPECIAL = "special"


class SessionStatus(str, Enum):
    """세션 상태"""
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"


class ParticipationType(str, Enum):
    """참가 타입"""
    MENS_DOUBLES = "mens_doubles"
    MIXED_DOUBLES = "mixed_doubles"
    SINGLES = "singles"


class Event(Model):
    """일정 모델"""

    id = fields.IntField(pk=True)
    club = fields.ForeignKeyField(
        "models.Club",
        related_name="events",
        on_delete=fields.CASCADE
    )
    title = fields.CharField(max_length=200)
    event_type = fields.CharEnumField(EventType, default=EventType.REGULAR)
    recurrence_rule = fields.CharField(max_length=500, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    # 관계
    sessions: fields.ReverseRelation["Session"]

    class Meta:
        table = "events"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.title} ({self.event_type})"


class SessionConfig(Model):
    """세션 설정 템플릿"""

    id = fields.IntField(pk=True)
    club = fields.ForeignKeyField(
        "models.Club",
        related_name="session_configs",
        on_delete=fields.CASCADE
    )
    name = fields.CharField(max_length=200)
    num_courts = fields.IntField()
    match_duration_minutes = fields.IntField()
    break_duration_minutes = fields.IntField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    # 관계
    sessions: fields.ReverseRelation["Session"]

    class Meta:
        table = "session_configs"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name


class Session(Model):
    """세션 모델"""

    id = fields.IntField(pk=True)
    event = fields.ForeignKeyField(
        "models.Event",
        related_name="sessions",
        on_delete=fields.CASCADE
    )
    config = fields.ForeignKeyField(
        "models.SessionConfig",
        related_name="sessions",
        on_delete=fields.SET_NULL,
        null=True
    )
    date = fields.DateField()
    start_time = fields.TimeField()
    end_time = fields.TimeField()
    num_courts = fields.IntField()
    match_duration_minutes = fields.IntField()
    break_duration_minutes = fields.IntField(null=True)
    status = fields.CharEnumField(SessionStatus, default=SessionStatus.DRAFT)
    created_at = fields.DatetimeField(auto_now_add=True)

    # 관계
    participants: fields.ReverseRelation["SessionParticipant"]
    matches: fields.ReverseRelation["Match"]

    class Meta:
        table = "sessions"
        ordering = ["-date", "-start_time"]

    def __str__(self) -> str:
        return f"{self.event.title} - {self.date} {self.start_time}"


class SessionParticipant(Model):
    """세션 참가자"""

    id = fields.IntField(pk=True)
    session = fields.ForeignKeyField(
        "models.Session",
        related_name="participants",
        on_delete=fields.CASCADE
    )
    club_member = fields.ForeignKeyField(
        "models.ClubMember",
        related_name="session_participations",
        on_delete=fields.CASCADE
    )
    participation_type = fields.CharEnumField(ParticipationType)
    arrived_at = fields.DatetimeField(null=True)

    class Meta:
        table = "session_participants"
        ordering = ["arrived_at"]

    def __str__(self) -> str:
        return f"{self.club_member.user.name} @ {self.session}"
