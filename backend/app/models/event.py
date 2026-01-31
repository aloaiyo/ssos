"""
일정 및 세션 모델
"""
from tortoise import fields
from app.models.base import BaseModel
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


class SessionType(str, Enum):
    """세션 타입 (경기 방식)"""
    LEAGUE = "league"          # 리그전
    TOURNAMENT = "tournament"  # 토너먼트


class ParticipationType(str, Enum):
    """참가 타입 (경기 종류)"""
    MENS_DOUBLES = "mens_doubles"
    MIXED_DOUBLES = "mixed_doubles"
    SINGLES = "singles"


class ParticipantCategory(str, Enum):
    """참가자 유형"""
    MEMBER = "member"        # 정회원 (동호회 가입)
    GUEST = "guest"          # 게스트 (시스템 미가입)
    ASSOCIATE = "associate"  # 준회원 (시스템 가입, 동호회 미가입)


class Event(BaseModel):
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


class SessionConfig(BaseModel):
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


class Session(BaseModel):
    """
    세션 모델

    시간 저장 방식:
    - start_datetime, end_datetime: UTC로 저장 (타임존 명확)
    - date, start_time, end_time 프로퍼티: KST 기준으로 반환 (하위 호환)
    """

    id = fields.IntField(pk=True)
    event = fields.ForeignKeyField(
        "models.Event",
        related_name="sessions",
        on_delete=fields.CASCADE,
        null=True  # 시즌에 직접 연결된 세션은 event 없음
    )
    season = fields.ForeignKeyField(
        "models.Season",
        related_name="sessions",
        on_delete=fields.CASCADE,
        null=True  # 시즌 없이 단독 세션 가능
    )
    config = fields.ForeignKeyField(
        "models.SessionConfig",
        related_name="sessions",
        on_delete=fields.SET_NULL,
        null=True
    )
    title = fields.CharField(max_length=200, null=True)  # 세션 제목

    # 시간: UTC로 저장 (타임존 명확)
    start_datetime = fields.DatetimeField()  # 세션 시작 시간 (UTC)
    end_datetime = fields.DatetimeField()    # 세션 종료 시간 (UTC)

    location = fields.CharField(max_length=300, null=True)  # 장소
    num_courts = fields.IntField()
    match_duration_minutes = fields.IntField()
    break_duration_minutes = fields.IntField(null=True)
    session_type = fields.CharEnumField(SessionType, default=SessionType.LEAGUE)  # 리그/토너먼트
    status = fields.CharEnumField(SessionStatus, default=SessionStatus.DRAFT)
    created_at = fields.DatetimeField(auto_now_add=True)

    @property
    def date(self):
        """세션 날짜 (KST 기준)"""
        from app.core.timezone import to_kst
        return to_kst(self.start_datetime).date()

    @property
    def start_time(self):
        """세션 시작 시간 (KST 기준)"""
        from app.core.timezone import to_kst
        return to_kst(self.start_datetime).time()

    @property
    def end_time(self):
        """세션 종료 시간 (KST 기준)"""
        from app.core.timezone import to_kst
        return to_kst(self.end_datetime).time()

    # 관계
    participants: fields.ReverseRelation["SessionParticipant"]
    matches: fields.ReverseRelation["Match"]

    class Meta:
        table = "sessions"
        ordering = ["-start_datetime"]

    def __str__(self) -> str:
        return f"Session #{self.id} - {self.date} {self.start_time}"


class SessionParticipant(BaseModel):
    """
    세션 참가자
    - 정회원: club_member 설정
    - 게스트: guest 설정
    - 준회원: user 설정 (동호회 미가입 유저)
    """

    id = fields.IntField(pk=True)
    session = fields.ForeignKeyField(
        "models.Session",
        related_name="participants",
        on_delete=fields.CASCADE
    )

    # 참가자 유형에 따라 하나만 설정됨
    club_member = fields.ForeignKeyField(
        "models.ClubMember",
        related_name="session_participations",
        on_delete=fields.CASCADE,
        null=True  # 게스트/준회원인 경우 null
    )
    guest = fields.ForeignKeyField(
        "models.Guest",
        related_name="session_participations",
        on_delete=fields.CASCADE,
        null=True  # 정회원/준회원인 경우 null
    )
    user = fields.ForeignKeyField(
        "models.User",
        related_name="associate_session_participations",
        on_delete=fields.CASCADE,
        null=True  # 정회원/게스트인 경우 null (준회원용)
    )

    # 참가자 유형
    participant_category = fields.CharEnumField(
        ParticipantCategory,
        default=ParticipantCategory.MEMBER
    )
    participation_type = fields.CharEnumField(ParticipationType, null=True)
    arrived_at = fields.DatetimeField(null=True)

    class Meta:
        table = "session_participants"
        ordering = ["arrived_at"]

    def __str__(self) -> str:
        name = self.get_participant_name()
        return f"{name} @ {self.session}"

    def get_participant_name(self) -> str:
        """참가자 이름 반환"""
        if self.club_member:
            return self.club_member.user.name
        elif self.guest:
            return f"{self.guest.name} (게스트)"
        elif self.user:
            return f"{self.user.name} (준회원)"
        return "Unknown"

    def get_participant_gender(self) -> str:
        """참가자 성별 반환"""
        if self.club_member:
            return self.club_member.gender.value
        elif self.guest:
            return self.guest.gender.value
        elif self.user:
            return self.user.gender or "male"
        return "male"
