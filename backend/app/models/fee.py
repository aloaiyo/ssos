"""
회비 관련 모델
"""
from tortoise import fields
from app.models.base import BaseModel
from enum import Enum


class PaymentStatus(str, Enum):
    """납부 상태"""
    PENDING = "pending"      # 미납
    PAID = "paid"            # 완납
    PARTIAL = "partial"      # 일부 납부
    EXEMPT = "exempt"        # 면제


class FeeType(str, Enum):
    """회비 타입"""
    MONTHLY = "monthly"      # 월회비
    YEARLY = "yearly"        # 연회비
    SESSION = "session"      # 세션별
    ONE_TIME = "one_time"    # 일회성


class FeeSetting(BaseModel):
    """회비 설정"""

    id = fields.IntField(pk=True)
    club = fields.ForeignKeyField(
        "models.Club",
        related_name="fee_settings",
        on_delete=fields.CASCADE
    )
    name = fields.CharField(max_length=100)  # 예: "2024년 월회비"
    fee_type = fields.CharEnumField(FeeType, default=FeeType.MONTHLY)
    amount = fields.IntField()  # 금액 (원)
    description = fields.TextField(null=True)
    is_active = fields.BooleanField(default=True)
    due_day = fields.IntField(default=1)  # 납부 기한일 (매월 n일)

    class Meta:
        table = "fee_settings"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} ({self.amount}원)"


class FeePayment(BaseModel):
    """회비 납부 기록"""

    id = fields.IntField(pk=True)
    fee_setting = fields.ForeignKeyField(
        "models.FeeSetting",
        related_name="payments",
        on_delete=fields.CASCADE
    )
    club_member = fields.ForeignKeyField(
        "models.ClubMember",
        related_name="fee_payments",
        on_delete=fields.CASCADE
    )
    # 납부 대상 기간 (예: 2024년 1월)
    target_year = fields.IntField()
    target_month = fields.IntField(null=True)  # 연회비인 경우 null

    amount_due = fields.IntField()  # 납부해야 할 금액
    amount_paid = fields.IntField(default=0)  # 납부한 금액
    status = fields.CharEnumField(PaymentStatus, default=PaymentStatus.PENDING)

    paid_at = fields.DatetimeField(null=True)  # 납부 완료 시점
    note = fields.TextField(null=True)  # 메모

    recorded_by = fields.ForeignKeyField(
        "models.User",
        related_name="recorded_payments",
        on_delete=fields.SET_NULL,
        null=True
    )

    class Meta:
        table = "fee_payments"
        ordering = ["-target_year", "-target_month"]
        unique_together = (("fee_setting", "club_member", "target_year", "target_month"),)

    def __str__(self) -> str:
        return f"{self.club_member} - {self.target_year}/{self.target_month}"
