"""
동호회 회원 스키마
"""
from pydantic import BaseModel
from datetime import datetime
from app.models.member import MemberRole, Gender, PreferredType
from typing import Optional


class ClubMemberBase(BaseModel):
    """회원 기본 스키마"""
    gender: Gender
    preferred_type: PreferredType


class ClubMemberCreate(ClubMemberBase):
    """회원 생성 스키마"""
    user_id: int


class ClubMemberUpdate(BaseModel):
    """회원 수정 스키마"""
    role: Optional[MemberRole] = None
    gender: Optional[Gender] = None
    preferred_type: Optional[PreferredType] = None


class ClubMemberResponse(ClubMemberBase):
    """회원 응답 스키마"""
    id: int
    club_id: int
    user_id: int
    role: MemberRole
    joined_at: datetime

    class Config:
        from_attributes = True


class ClubMemberDetailResponse(ClubMemberResponse):
    """회원 상세 응답 스키마 (사용자 정보 포함)"""
    user_name: str
    user_email: str
