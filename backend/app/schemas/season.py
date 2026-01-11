"""
시즌 스키마
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime, date
from app.models.season import SeasonStatus
from typing import Optional, List


class SeasonBase(BaseModel):
    """시즌 기본 스키마"""
    name: str
    description: Optional[str] = None
    start_date: date
    end_date: date


class SeasonCreate(SeasonBase):
    """시즌 생성 스키마"""
    pass


class SeasonUpdate(BaseModel):
    """시즌 수정 스키마"""
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[SeasonStatus] = None


class SeasonResponse(SeasonBase):
    """시즌 응답 스키마"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    club_id: int
    status: SeasonStatus
    created_at: datetime


class SeasonWithStatsResponse(SeasonResponse):
    """시즌 통계 포함 응답 스키마"""
    total_sessions: int = 0
    total_matches: int = 0
    total_participants: int = 0


# 시즌별 랭킹 스키마
class SeasonRankingBase(BaseModel):
    """시즌 랭킹 기본 스키마"""
    total_matches: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    points: int = 0


class SeasonRankingResponse(SeasonRankingBase):
    """시즌 랭킹 응답 스키마"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    season_id: int
    club_member_id: int
    rank: Optional[int] = None
    win_rate: float = 0.0
    last_updated: datetime

    # 추가 정보 (조인 결과)
    member_name: Optional[str] = None
    member_nickname: Optional[str] = None


class SeasonRankingListResponse(BaseModel):
    """시즌 랭킹 목록 응답"""
    season: SeasonResponse
    rankings: List[SeasonRankingResponse]
