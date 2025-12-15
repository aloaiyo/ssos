"""
동호회 정기 활동 스케줄 모델
"""
from tortoise import fields
from app.models.base import BaseModel


class ClubSchedule(BaseModel):
    """동호회 정기 활동 스케줄"""

    id = fields.IntField(pk=True)
    club = fields.ForeignKeyField(
        "models.Club",
        related_name="schedules",
        on_delete=fields.CASCADE
    )
    day_of_week = fields.IntField()  # 0=월, 1=화, ..., 6=일
    start_time = fields.TimeField()
    end_time = fields.TimeField()
    is_active = fields.BooleanField(default=True)

    class Meta:
        table = "club_schedules"
        ordering = ["day_of_week", "start_time"]
        unique_together = [("club", "day_of_week")]

    def __str__(self) -> str:
        days = ["월", "화", "수", "목", "금", "토", "일"]
        return f"{days[self.day_of_week]}요일 {self.start_time}-{self.end_time}"
