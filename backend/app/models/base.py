"""
기본 모델
"""
from tortoise import fields
from tortoise.models import Model


class BaseModel(Model):
    """
    모든 모델의 기본이 되는 추상 모델
    생성일, 수정일, 삭제 여부를 포함
    """
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    is_deleted = fields.BooleanField(default=False)

    class Meta:
        abstract = True
