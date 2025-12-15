"""
동호회 스케줄 스키마
"""
from pydantic import BaseModel, ConfigDict, field_validator
from datetime import time
from typing import Optional, List


class ScheduleBase(BaseModel):
    """스케줄 기본 스키마"""
    day_of_week: int  # 0=월, 1=화, ..., 6=일
    start_time: time
    end_time: time
    is_active: bool = True

    @field_validator('day_of_week')
    @classmethod
    def validate_day_of_week(cls, v):
        if v < 0 or v > 6:
            raise ValueError('day_of_week must be between 0 and 6')
        return v

    @field_validator('end_time')
    @classmethod
    def validate_end_time(cls, v, info):
        start_time = info.data.get('start_time')
        if start_time and v <= start_time:
            raise ValueError('end_time must be after start_time')
        return v


class ScheduleCreate(ScheduleBase):
    """스케줄 생성 스키마"""
    pass


class ScheduleUpdate(BaseModel):
    """스케줄 수정 스키마"""
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_active: Optional[bool] = None


class ScheduleResponse(ScheduleBase):
    """스케줄 응답 스키마"""
    id: int

    model_config = ConfigDict(from_attributes=True)


class ScheduleBulkUpdate(BaseModel):
    """스케줄 일괄 업데이트 스키마 (프론트엔드에서 한번에 전송)"""
    schedules: List[ScheduleCreate]
