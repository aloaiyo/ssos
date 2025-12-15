"""
동호회 스키마
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime, time
from typing import Optional, List
from app.schemas.schedule import ScheduleCreate, ScheduleResponse


class ClubBase(BaseModel):
    """동호회 기본 스키마"""
    name: str
    description: Optional[str] = None


class ClubCreate(ClubBase):
    """동호회 생성 스키마"""
    # 기본 정보
    default_num_courts: Optional[int] = None
    default_match_duration: Optional[int] = 30
    location: Optional[str] = None
    # 정기 활동 스케줄 (여러 요일별 시간)
    schedules: Optional[List[ScheduleCreate]] = None


class ClubUpdate(BaseModel):
    """동호회 수정 스키마"""
    name: Optional[str] = None
    description: Optional[str] = None
    # 기본 정보
    default_num_courts: Optional[int] = None
    default_match_duration: Optional[int] = None
    location: Optional[str] = None
    # 정기 활동 스케줄 (전체 교체)
    schedules: Optional[List[ScheduleCreate]] = None


class ClubResponse(ClubBase):
    """동호회 응답 스키마"""
    id: int
    created_by_id: int
    created_at: datetime
    modified_at: datetime
    is_deleted: bool
    # 기본 정보
    default_num_courts: Optional[int] = None
    default_match_duration: Optional[int] = None
    location: Optional[str] = None
    # 정기 활동 스케줄
    schedules: List[ScheduleResponse] = []

    model_config = ConfigDict(from_attributes=True)
