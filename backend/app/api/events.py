"""
일정 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.event import EventCreate, EventResponse, EventUpdate
from app.models.event import Event
from app.models.club import Club
from app.models.user import User
from app.core.dependencies import get_current_active_user

router = APIRouter(prefix="/events", tags=["일정"])


@router.get("", response_model=List[EventResponse])
async def list_events(
    club_id: int,
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100
):
    """일정 목록 조회"""
    events = await Event.filter(club_id=club_id).offset(skip).limit(limit)
    return [EventResponse.model_validate(event) for event in events]


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    current_user: User = Depends(get_current_active_user)
):
    """일정 생성"""
    club = await Club.get_or_none(id=event_data.club_id)
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="동호회를 찾을 수 없습니다"
        )

    event = await Event.create(
        club_id=event_data.club_id,
        title=event_data.title,
        event_type=event_data.event_type,
        recurrence_rule=event_data.recurrence_rule
    )

    return EventResponse.model_validate(event)


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """일정 상세 조회"""
    event = await Event.get_or_none(id=event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="일정을 찾을 수 없습니다"
        )
    return EventResponse.model_validate(event)


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    event_data: EventUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """일정 수정"""
    event = await Event.get_or_none(id=event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="일정을 찾을 수 없습니다"
        )

    # 수정
    if event_data.title is not None:
        event.title = event_data.title
    if event_data.event_type is not None:
        event.event_type = event_data.event_type
    if event_data.recurrence_rule is not None:
        event.recurrence_rule = event_data.recurrence_rule

    await event.save()
    return EventResponse.model_validate(event)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """일정 삭제"""
    event = await Event.get_or_none(id=event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="일정을 찾을 수 없습니다"
        )

    await event.delete()
