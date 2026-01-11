"""
게스트 모델
- 매니저가 생성한 미가입 참가자
- 나중에 서비스 가입 시 ClubMember와 연결 가능
"""
from tortoise import fields
from app.models.base import BaseModel
from app.models.member import Gender


class Guest(BaseModel):
    """
    게스트 모델 (매니저가 생성한 미가입 참가자)

    - 서비스에 가입하지 않은 외부 참가자
    - 매니저가 직접 생성하여 관리
    - 나중에 해당 게스트가 서비스에 가입하면 ClubMember와 연결
    - 연결 시 경기 기록이 회원 기록으로 이전됨
    """

    id = fields.IntField(pk=True)
    club = fields.ForeignKeyField(
        "models.Club",
        related_name="guests",
        on_delete=fields.CASCADE
    )
    name = fields.CharField(max_length=100)
    gender = fields.CharEnumField(Gender)
    phone = fields.CharField(max_length=20, null=True)  # 연락처 (선택)
    notes = fields.TextField(null=True)  # 메모

    # 연결 정보
    linked_member = fields.ForeignKeyField(
        "models.ClubMember",
        related_name="linked_guest",
        null=True,
        on_delete=fields.SET_NULL,
        description="연결된 회원 (서비스 가입 시 연결)"
    )
    created_by = fields.ForeignKeyField(
        "models.ClubMember",
        related_name="created_guests",
        null=True,
        on_delete=fields.SET_NULL,
        description="생성한 매니저"
    )

    # 통계 (게스트도 기록 관리)
    total_games = fields.IntField(default=0)
    wins = fields.IntField(default=0)
    losses = fields.IntField(default=0)
    draws = fields.IntField(default=0)

    class Meta:
        table = "guests"
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} (게스트)"

    @property
    def is_linked(self) -> bool:
        """회원과 연결되었는지 여부"""
        return self.linked_member_id is not None

    @property
    def win_rate(self) -> float:
        """승률 계산"""
        if self.total_games == 0:
            return 0.0
        return round(self.wins / self.total_games * 100, 1)
