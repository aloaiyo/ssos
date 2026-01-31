"""
일정 및 세션 스키마

시간 처리 규칙:
- API 요청: date + start_time + end_time (KST 기준으로 해석)
- API 응답: start_datetime + end_datetime (KST로 변환) + date/start_time/end_time (하위 호환)
- DB 저장: start_datetime + end_datetime (UTC)
"""
from pydantic import BaseModel, ConfigDict, field_validator, model_validator
from datetime import date, time, datetime
from app.models.event import EventType, SessionStatus, SessionType, ParticipationType
from typing import Optional, List
from app.core.timezone import KSTDatetime, OptionalKSTDatetime, KST, to_utc


class EventBase(BaseModel):
    """일정 기본 스키마"""
    title: str
    event_type: EventType = EventType.REGULAR
    recurrence_rule: Optional[str] = None


class EventCreate(EventBase):
    """일정 생성 스키마"""
    # club_id는 URL path에서 제공되므로 optional
    club_id: Optional[int] = None


class EventUpdate(BaseModel):
    """일정 수정 스키마"""
    title: Optional[str] = None
    event_type: Optional[EventType] = None
    recurrence_rule: Optional[str] = None


class EventResponse(EventBase):
    """일정 응답 스키마"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    club_id: int
    created_at: KSTDatetime


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
    model_config = ConfigDict(from_attributes=True)

    id: int
    club_id: int
    created_at: KSTDatetime


class SessionCreate(BaseModel):
    """
    세션 생성 스키마

    프론트엔드에서 date + start_time + end_time을 KST 기준으로 전송
    백엔드에서 UTC datetime으로 변환하여 저장
    """
    title: Optional[str] = None
    date: date                          # 세션 날짜 (KST 기준)
    start_time: time                    # 시작 시간 (KST 기준, 예: 09:00)
    end_time: time                      # 종료 시간 (KST 기준, 예: 12:00)
    location: Optional[str] = None
    num_courts: int
    match_duration_minutes: int
    break_duration_minutes: Optional[int] = None
    session_type: SessionType = SessionType.LEAGUE
    event_id: Optional[int] = None
    season_id: Optional[int] = None
    config_id: Optional[int] = None

    def to_utc_datetimes(self) -> tuple[datetime, datetime]:
        """date + time을 UTC datetime으로 변환"""
        # KST datetime 생성
        start_kst = datetime.combine(self.date, self.start_time, tzinfo=KST)
        end_kst = datetime.combine(self.date, self.end_time, tzinfo=KST)

        # 종료 시간이 시작 시간보다 이른 경우 (자정 넘김)
        if self.end_time <= self.start_time:
            from datetime import timedelta
            end_kst = end_kst + timedelta(days=1)

        # UTC로 변환
        return to_utc(start_kst), to_utc(end_kst)


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

    def to_utc_datetimes(self, current_date: date, current_start: time, current_end: time) -> tuple[Optional[datetime], Optional[datetime]]:
        """
        수정된 필드만 UTC datetime으로 변환
        현재 값과 새 값을 조합하여 계산
        """
        # 새 값이 없으면 None 반환
        if self.date is None and self.start_time is None and self.end_time is None:
            return None, None

        # 새 값 또는 현재 값 사용
        new_date = self.date or current_date
        new_start = self.start_time or current_start
        new_end = self.end_time or current_end

        # KST datetime 생성
        start_kst = datetime.combine(new_date, new_start, tzinfo=KST)
        end_kst = datetime.combine(new_date, new_end, tzinfo=KST)

        # 종료 시간이 시작 시간보다 이른 경우 (자정 넘김)
        if new_end <= new_start:
            from datetime import timedelta
            end_kst = end_kst + timedelta(days=1)

        return to_utc(start_kst), to_utc(end_kst)


class SessionResponse(BaseModel):
    """
    세션 응답 스키마

    start_datetime, end_datetime: 정확한 UTC→KST 변환된 datetime
    date, start_time, end_time: 하위 호환용 (KST 기준)
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: Optional[str] = None
    # UTC datetime (응답 시 KST로 변환)
    start_datetime: KSTDatetime
    end_datetime: KSTDatetime
    # 하위 호환용 필드 (프로퍼티에서 자동 계산)
    date: date
    start_time: time
    end_time: time
    location: Optional[str] = None
    num_courts: int
    match_duration_minutes: int
    break_duration_minutes: Optional[int] = None
    session_type: SessionType
    event_id: Optional[int] = None
    season_id: Optional[int] = None
    config_id: Optional[int] = None
    status: SessionStatus
    created_at: KSTDatetime


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
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    club_member_id: int
    participation_type: ParticipationType
    arrived_at: OptionalKSTDatetime = None
