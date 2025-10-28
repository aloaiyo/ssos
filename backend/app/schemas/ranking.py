"""
랭킹 스키마
"""
from pydantic import BaseModel
from datetime import datetime


class RankingBase(BaseModel):
    """랭킹 기본 스키마"""
    total_matches: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    points: int = 0


class RankingResponse(RankingBase):
    """랭킹 응답 스키마"""
    id: int
    club_id: int
    club_member_id: int
    last_updated: datetime
    win_rate: float

    class Config:
        from_attributes = True


class RankingDetailResponse(RankingResponse):
    """랭킹 상세 응답 스키마 (회원 정보 포함)"""
    member_name: str
    member_email: str
