"""
클럽 공지사항 모델
"""
from tortoise import fields
from app.models.base import BaseModel
from enum import Enum


class AnnouncementType(str, Enum):
    """공지 타입"""
    GENERAL = "general"      # 일반 공지
    IMPORTANT = "important"  # 중요 공지
    EVENT = "event"          # 이벤트


class Announcement(BaseModel):
    """클럽 공지사항"""

    id = fields.IntField(pk=True)
    club = fields.ForeignKeyField(
        "models.Club",
        related_name="announcements",
        on_delete=fields.CASCADE
    )
    author = fields.ForeignKeyField(
        "models.User",
        related_name="authored_announcements",
        on_delete=fields.SET_NULL,
        null=True
    )
    title = fields.CharField(max_length=200)
    content = fields.TextField()
    announcement_type = fields.CharEnumField(AnnouncementType, default=AnnouncementType.GENERAL)
    is_pinned = fields.BooleanField(default=False)  # 상단 고정
    views = fields.IntField(default=0)

    class Meta:
        table = "announcements"
        ordering = ["-is_pinned", "-created_at"]

    def __str__(self) -> str:
        return f"[{self.announcement_type.value}] {self.title}"
