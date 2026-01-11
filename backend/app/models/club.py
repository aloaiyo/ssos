"""
동호회 모델
"""
from tortoise import fields
from app.models.base import BaseModel


class Club(BaseModel):
    """동호회 모델"""

    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=200)
    description = fields.TextField(null=True)
    created_by = fields.ForeignKeyField(
        "models.User",
        related_name="created_clubs",
        on_delete=fields.CASCADE
    )

    # 기본 정보 (정기 활동 설정)
    default_day_of_week = fields.IntField(null=True)  # 0=월, 1=화, ..., 6=일
    default_start_time = fields.TimeField(null=True)  # 기본 시작 시간
    default_end_time = fields.TimeField(null=True)    # 기본 종료 시간
    default_num_courts = fields.IntField(null=True)   # 기본 코트 수
    default_match_duration = fields.IntField(default=30)  # 기본 경기 시간 (분)
    location = fields.CharField(max_length=500, null=True)  # 활동 장소

    # 가입 설정
    is_join_allowed = fields.BooleanField(default=True)  # 가입 허용 여부
    requires_approval = fields.BooleanField(default=False)  # 가입 승인 필요 여부

    # 관계
    members: fields.ReverseRelation["ClubMember"]
    events: fields.ReverseRelation["Event"]
    session_configs: fields.ReverseRelation["SessionConfig"]
    rankings: fields.ReverseRelation["Ranking"]
    schedules: fields.ReverseRelation["ClubSchedule"]

    class Meta:
        table = "clubs"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name
