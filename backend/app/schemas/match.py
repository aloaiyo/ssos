"""
경기 스키마

시간 처리 규칙:
- scheduled_datetime: 경기 예정 시간 (UTC 저장, KST 응답)
- scheduled_time: 하위 호환용 (KST 기준 시간만)
"""
from pydantic import BaseModel, ConfigDict
from datetime import time, datetime
from app.models.match import MatchType, MatchStatus, Team
from typing import Optional, List, Dict, Any
from app.core.timezone import KSTDatetime, OptionalKSTDatetime


class MatchCreate(BaseModel):
    """경기 생성 스키마 (내부 API용, 세션에서 생성 시 사용)"""
    session_id: int
    match_number: int
    court_number: int
    scheduled_datetime: datetime  # UTC datetime
    match_type: MatchType


class MatchUpdate(BaseModel):
    """경기 수정 스키마"""
    court_number: Optional[int] = None
    scheduled_datetime: Optional[datetime] = None  # UTC datetime
    status: Optional[MatchStatus] = None


class MatchResponse(BaseModel):
    """경기 응답 스키마"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    match_number: int
    court_number: int
    # UTC datetime (응답 시 KST로 변환)
    scheduled_datetime: KSTDatetime
    # 하위 호환용 (프로퍼티에서 자동 계산)
    scheduled_time: time
    match_type: MatchType
    status: MatchStatus
    actual_start_time: OptionalKSTDatetime = None
    actual_end_time: OptionalKSTDatetime = None
    created_at: KSTDatetime


class MatchParticipantCreate(BaseModel):
    """경기 참가자 생성 스키마"""
    match_id: int
    club_member_id: int
    team: Team
    position: int


class MatchParticipantResponse(BaseModel):
    """경기 참가자 응답 스키마"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    match_id: int
    club_member_id: int
    team: Team
    position: int


class MatchResultBase(BaseModel):
    """경기 결과 기본 스키마"""
    team_a_score: int
    team_b_score: int
    sets_detail: Dict[str, Any]
    winner_team: Optional[Team] = None


class MatchResultCreate(MatchResultBase):
    """경기 결과 생성 스키마"""
    match_id: int


class MatchResultResponse(MatchResultBase):
    """경기 결과 응답 스키마"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    match_id: int
    recorded_by_id: Optional[int] = None
    recorded_at: KSTDatetime
