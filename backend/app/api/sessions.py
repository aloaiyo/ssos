"""
세션 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.event import (
    SessionCreate, SessionResponse, SessionUpdate,
    SessionParticipantCreate, SessionParticipantResponse
)
from app.models.event import Event, Session, SessionParticipant
from app.models.member import ClubMember
from app.models.user import User
from app.core.dependencies import get_current_active_user

router = APIRouter(prefix="/sessions", tags=["세션"])


@router.get("", response_model=List[SessionResponse])
async def list_sessions(
    event_id: int,
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100
):
    """세션 목록 조회"""
    sessions = await Session.filter(event_id=event_id).offset(skip).limit(limit)
    return [SessionResponse.model_validate(session) for session in sessions]


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    current_user: User = Depends(get_current_active_user)
):
    """세션 생성"""
    event = await Event.get_or_none(id=session_data.event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="일정을 찾을 수 없습니다"
        )

    session = await Session.create(
        event_id=session_data.event_id,
        config_id=session_data.config_id,
        date=session_data.date,
        start_time=session_data.start_time,
        end_time=session_data.end_time,
        num_courts=session_data.num_courts,
        match_duration_minutes=session_data.match_duration_minutes,
        break_duration_minutes=session_data.break_duration_minutes
    )

    return SessionResponse.model_validate(session)


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """세션 상세 조회"""
    session = await Session.get_or_none(id=session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="세션을 찾을 수 없습니다"
        )
    return SessionResponse.model_validate(session)


@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: int,
    session_data: SessionUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """세션 수정"""
    session = await Session.get_or_none(id=session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="세션을 찾을 수 없습니다"
        )

    # 수정
    if session_data.date is not None:
        session.date = session_data.date
    if session_data.start_time is not None:
        session.start_time = session_data.start_time
    if session_data.end_time is not None:
        session.end_time = session_data.end_time
    if session_data.num_courts is not None:
        session.num_courts = session_data.num_courts
    if session_data.match_duration_minutes is not None:
        session.match_duration_minutes = session_data.match_duration_minutes
    if session_data.break_duration_minutes is not None:
        session.break_duration_minutes = session_data.break_duration_minutes
    if session_data.status is not None:
        session.status = session_data.status

    await session.save()
    return SessionResponse.model_validate(session)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """세션 삭제"""
    session = await Session.get_or_none(id=session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="세션을 찾을 수 없습니다"
        )

    await session.delete()


# 세션 참가자 관리
@router.get("/{session_id}/participants", response_model=List[SessionParticipantResponse])
async def list_session_participants(
    session_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """세션 참가자 목록 조회"""
    session = await Session.get_or_none(id=session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="세션을 찾을 수 없습니다"
        )

    participants = await SessionParticipant.filter(session_id=session_id)
    return [SessionParticipantResponse.model_validate(p) for p in participants]


@router.post("/{session_id}/participants", response_model=SessionParticipantResponse, status_code=status.HTTP_201_CREATED)
async def add_session_participant(
    session_id: int,
    participant_data: SessionParticipantCreate,
    current_user: User = Depends(get_current_active_user)
):
    """세션 참가자 추가"""
    session = await Session.get_or_none(id=session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="세션을 찾을 수 없습니다"
        )

    member = await ClubMember.get_or_none(id=participant_data.club_member_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="회원을 찾을 수 없습니다"
        )

    # 중복 확인
    existing = await SessionParticipant.get_or_none(
        session_id=session_id,
        club_member_id=participant_data.club_member_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 참가 신청된 회원입니다"
        )

    participant = await SessionParticipant.create(
        session_id=session_id,
        club_member_id=participant_data.club_member_id,
        participation_type=participant_data.participation_type
    )

    return SessionParticipantResponse.model_validate(participant)
