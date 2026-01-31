"""
경기 모델
"""
from tortoise import fields
from app.models.base import BaseModel
from enum import Enum


class MatchType(str, Enum):
    """경기 타입"""
    MENS_DOUBLES = "mens_doubles"
    WOMENS_DOUBLES = "womens_doubles"
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


class Match(BaseModel):
    """
    경기 모델

    시간 저장 방식:
    - scheduled_datetime: 예정 시작 시간 (UTC)
    - actual_start_time, actual_end_time: 실제 시작/종료 시간 (UTC)
    - scheduled_time 프로퍼티: KST 기준 시간만 반환 (하위 호환)
    """

    id = fields.IntField(pk=True)
    session = fields.ForeignKeyField(
        "models.Session",
        related_name="matches",
        on_delete=fields.CASCADE
    )
    match_number = fields.IntField()
    court_number = fields.IntField()
    scheduled_datetime = fields.DatetimeField()  # 예정 시작 시간 (UTC)
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

    @property
    def scheduled_time(self):
        """경기 예정 시간 (KST 기준, 하위 호환용)"""
        from app.core.timezone import to_kst
        return to_kst(self.scheduled_datetime).time()


class ParticipantCategory(str, Enum):
    """참가자 유형"""
    MEMBER = "member"        # 정회원 (동호회 가입)
    GUEST = "guest"          # 게스트 (시스템 미가입)
    ASSOCIATE = "associate"  # 준회원 (시스템 가입, 동호회 미가입)


class MatchParticipant(BaseModel):
    """
    경기 참가자
    - 정회원: club_member 설정
    - 게스트: guest 설정
    - 준회원: user 설정 (동호회 미가입 유저)
    """

    id = fields.IntField(pk=True)
    match = fields.ForeignKeyField(
        "models.Match",
        related_name="participants",
        on_delete=fields.CASCADE
    )

    # 참가자 유형에 따라 하나만 설정됨
    club_member = fields.ForeignKeyField(
        "models.ClubMember",
        related_name="match_participations",
        on_delete=fields.CASCADE,
        null=True  # 게스트/준회원인 경우 null
    )
    guest = fields.ForeignKeyField(
        "models.Guest",
        related_name="match_participations",
        on_delete=fields.CASCADE,
        null=True  # 정회원/준회원인 경우 null
    )
    user = fields.ForeignKeyField(
        "models.User",
        related_name="associate_match_participations",
        on_delete=fields.CASCADE,
        null=True  # 정회원/게스트인 경우 null (준회원용)
    )

    # 참가자 유형
    participant_category = fields.CharEnumField(
        ParticipantCategory,
        default=ParticipantCategory.MEMBER
    )
    team = fields.CharEnumField(Team)
    position = fields.IntField()  # 1 or 2

    class Meta:
        table = "match_participants"
        ordering = ["team", "position"]

    def __str__(self) -> str:
        name = self.get_participant_name()
        return f"{name} - Team {self.team} (Pos {self.position})"

    def get_participant_name(self) -> str:
        """참가자 이름 반환"""
        if self.club_member:
            return self.club_member.user.name
        elif self.guest:
            return self.guest.name
        elif self.user:
            return self.user.name
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

    def get_participant_id(self) -> int:
        """참가자 고유 ID 반환 (통계용)"""
        if self.club_member:
            return self.club_member_id
        elif self.guest:
            return self.guest_id
        elif self.user:
            return self.user_id
        return 0


class MatchResult(BaseModel):
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
