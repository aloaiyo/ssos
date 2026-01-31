"""
동호회 스키마
"""
from pydantic import BaseModel, ConfigDict
from datetime import time
from typing import Optional, List
from app.schemas.schedule import ScheduleCreate, ScheduleResponse
from app.core.timezone import KSTDatetime


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
    # 가입 설정
    is_join_allowed: bool = True
    requires_approval: bool = False
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
    # 가입 설정
    is_join_allowed: Optional[bool] = None
    requires_approval: Optional[bool] = None
    # 정기 활동 스케줄 (전체 교체)
    schedules: Optional[List[ScheduleCreate]] = None


class ClubResponse(ClubBase):
    """동호회 응답 스키마"""
    id: int
    created_by_id: int
    created_at: KSTDatetime
    modified_at: KSTDatetime
    is_deleted: bool
    # 기본 정보
    default_num_courts: Optional[int] = None
    default_match_duration: Optional[int] = None
    location: Optional[str] = None
    # 가입 설정
    is_join_allowed: bool = True
    requires_approval: bool = False
    # 정기 활동 스케줄
    schedules: List[ScheduleResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ClubSearchResponse(ClubBase):
    """동호회 검색 응답 스키마 (회원수, 가입상태 포함)"""
    id: int
    created_at: KSTDatetime
    location: Optional[str] = None
    # 가입 설정
    is_join_allowed: bool = True
    requires_approval: bool = False
    # 추가 정보
    member_count: int = 0
    my_status: Optional[str] = None  # None, 'active', 'pending', 'left', 'banned'

    model_config = ConfigDict(from_attributes=True)
