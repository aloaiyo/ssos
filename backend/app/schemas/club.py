"""
동호회 스키마
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ClubBase(BaseModel):
    """동호회 기본 스키마"""
    name: str
    description: Optional[str] = None


class ClubCreate(ClubBase):
    """동호회 생성 스키마"""
    pass


class ClubUpdate(BaseModel):
    """동호회 수정 스키마"""
    name: Optional[str] = None
    description: Optional[str] = None


class ClubResponse(ClubBase):
    """동호회 응답 스키마"""
    id: int
    created_by_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
