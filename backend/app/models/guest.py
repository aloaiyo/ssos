"""
게스트 모델
"""
from tortoise import fields
from app.models.base import BaseModel
from app.models.member import Gender


class Guest(BaseModel):
    """
    게스트 모델
    - 시스템에 가입하지 않은 외부 참가자
    - 이름과 성별만 저장
    - 동호회별로 관리
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
    def win_rate(self) -> float:
        """승률 계산"""
        if self.total_games == 0:
            return 0.0
        return round(self.wins / self.total_games * 100, 1)
