"""
일정 및 세션 스키마
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime, date, time
from app.models.event import EventType, SessionStatus, SessionType, ParticipationType
from typing import Optional, List


class EventBase(BaseModel):
    """일정 기본 스키마"""
    title: str
    event_type: EventType = EventType.REGULAR
    recurrence_rule: Optional[str] = None


class EventCreate(EventBase):
    """일정 생성 스키마"""
    club_id: int


class EventUpdate(BaseModel):
    """일정 수정 스키마"""
    title: Optional[str] = None
    event_type: Optional[EventType] = None
    recurrence_rule: Optional[str] = None


class EventResponse(EventBase):
    """일정 응답 스키마"""
    id: int
    club_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class SessionConfigBase(BaseModel):
    """세션 설정 기본 스키마"""
    name: str
    num_courts: int
    match_duration_minutes: int
    break_duration_minutes: Optional[int] = None


class SessionConfigCreate(SessionConfigBase):
    """세션 설정 생성 스키마"""
    club_id: int


class SessionConfigResponse(SessionConfigBase):
    """세션 설정 응답 스키마"""
    id: int
    club_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class SessionBase(BaseModel):
    """세션 기본 스키마"""
    title: Optional[str] = None
    date: date
    start_time: time
    end_time: time
    location: Optional[str] = None
    num_courts: int
    match_duration_minutes: int
    break_duration_minutes: Optional[int] = None
    session_type: SessionType = SessionType.LEAGUE


class SessionCreate(SessionBase):
    """세션 생성 스키마"""
    event_id: Optional[int] = None  # 이벤트 또는 시즌에 연결
    season_id: Optional[int] = None
    config_id: Optional[int] = None


class SessionUpdate(BaseModel):
    """세션 수정 스키마"""
    title: Optional[str] = None
    date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    location: Optional[str] = None
    num_courts: Optional[int] = None
    match_duration_minutes: Optional[int] = None
    break_duration_minutes: Optional[int] = None
    session_type: Optional[SessionType] = None
    status: Optional[SessionStatus] = None


class SessionResponse(SessionBase):
    """세션 응답 스키마"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_id: Optional[int] = None
    season_id: Optional[int] = None
    config_id: Optional[int] = None
    status: SessionStatus
    created_at: datetime


class SessionWithDetailsResponse(SessionResponse):
    """세션 상세 응답 스키마 (참가자, 경기 수 포함)"""
    participant_count: int = 0
    match_count: int = 0
    season_name: Optional[str] = None


class SessionParticipantCreate(BaseModel):
    """세션 참가자 생성 스키마"""
    session_id: int
    club_member_id: int
    participation_type: ParticipationType


class SessionParticipantResponse(BaseModel):
    """세션 참가자 응답 스키마"""
    id: int
    session_id: int
    club_member_id: int
    participation_type: ParticipationType
    arrived_at: Optional[datetime] = None

    class Config:
        from_attributes = True
