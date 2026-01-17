"""
매칭 API

권한 체계:
- 매치 조회: 인증된 사용자 (세션 소속 클럽 멤버 확인)
- 매치 생성/수정/삭제: 클럽 매니저만 가능
- 결과 등록: 클럽 매니저만 가능
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.match import (
    MatchCreate, MatchResponse, MatchUpdate,
    MatchParticipantResponse,
    MatchResultCreate, MatchResultResponse
)
from app.models.match import Match, MatchParticipant, MatchResult
from app.models.event import Session
from app.models.user import User
from app.models.member import ClubMember, MemberRole, MemberStatus
from app.core.dependencies import get_current_active_user

router = APIRouter(prefix="/matches", tags=["매칭"])


async def get_session_with_club(session_id: int) -> Session:
    """세션 조회 및 클럽 정보 포함"""
    session = await Session.get_or_none(
        id=session_id, is_deleted=False
    ).prefetch_related("event__club")
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="세션을 찾을 수 없습니다"
        )
    return session


async def verify_club_manager(session: Session, user: User) -> ClubMember:
    """세션 소속 클럽의 매니저인지 확인"""
    club = session.event.club
    membership = await ClubMember.get_or_none(
        club_id=club.id,
        user_id=user.id,
        is_deleted=False
    )

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="클럽 멤버가 아닙니다"
        )

    if membership.status != MemberStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="활성 멤버가 아닙니다"
        )

    if membership.role != MemberRole.MANAGER and not user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="클럽 관리자 권한이 필요합니다"
        )

    return membership


async def verify_club_member(session: Session, user: User) -> ClubMember:
    """세션 소속 클럽의 멤버인지 확인"""
    club = session.event.club
    membership = await ClubMember.get_or_none(
        club_id=club.id,
        user_id=user.id,
        is_deleted=False
    )

    if not membership and not user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="클럽 멤버가 아닙니다"
        )

    if membership and membership.status != MemberStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="활성 멤버가 아닙니다"
        )

    return membership


@router.get("", response_model=List[MatchResponse])
async def list_matches(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100
):
    """매치 목록 조회 - 클럽 멤버만 가능"""
    session = await get_session_with_club(session_id)
    await verify_club_member(session, current_user)

    matches = await Match.filter(
        session_id=session_id, is_deleted=False
    ).offset(skip).limit(limit)
    return [MatchResponse.model_validate(match) for match in matches]


@router.post("", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
async def create_match(
    match_data: MatchCreate,
    current_user: User = Depends(get_current_active_user)
):
    """매치 생성 - 클럽 매니저만 가능"""
    session = await get_session_with_club(match_data.session_id)
    await verify_club_manager(session, current_user)

    match = await Match.create(
        session_id=match_data.session_id,
        match_number=match_data.match_number,
        court_number=match_data.court_number,
        scheduled_time=match_data.scheduled_time,
        match_type=match_data.match_type
    )

    return MatchResponse.model_validate(match)


@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(
    match_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """매치 상세 조회 - 클럽 멤버만 가능"""
    match = await Match.get_or_none(
        id=match_id, is_deleted=False
    ).prefetch_related("session__event__club")
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="매치를 찾을 수 없습니다"
        )

    await verify_club_member(match.session, current_user)
    return MatchResponse.model_validate(match)


@router.put("/{match_id}", response_model=MatchResponse)
async def update_match(
    match_id: int,
    match_data: MatchUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """매치 수정 - 클럽 매니저만 가능"""
    match = await Match.get_or_none(
        id=match_id, is_deleted=False
    ).prefetch_related("session__event__club")
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="매치를 찾을 수 없습니다"
        )

    await verify_club_manager(match.session, current_user)

    # 수정
    if match_data.court_number is not None:
        match.court_number = match_data.court_number
    if match_data.scheduled_time is not None:
        match.scheduled_time = match_data.scheduled_time
    if match_data.status is not None:
        match.status = match_data.status

    await match.save()
    return MatchResponse.model_validate(match)


@router.delete("/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_match(
    match_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """매치 삭제 (soft delete) - 클럽 매니저만 가능"""
    match = await Match.get_or_none(
        id=match_id, is_deleted=False
    ).prefetch_related("session__event__club")
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="매치를 찾을 수 없습니다"
        )

    await verify_club_manager(match.session, current_user)

    match.is_deleted = True
    await match.save()


# 매치 참가자
@router.get("/{match_id}/participants", response_model=List[MatchParticipantResponse])
async def list_match_participants(
    match_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """매치 참가자 목록 조회 - 클럽 멤버만 가능"""
    match = await Match.get_or_none(
        id=match_id, is_deleted=False
    ).prefetch_related("session__event__club")
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="매치를 찾을 수 없습니다"
        )

    await verify_club_member(match.session, current_user)

    participants = await MatchParticipant.filter(match_id=match_id, is_deleted=False)
    return [MatchParticipantResponse.model_validate(p) for p in participants]


# 매치 결과
@router.post("/{match_id}/result", response_model=MatchResultResponse, status_code=status.HTTP_201_CREATED)
async def create_match_result(
    match_id: int,
    result_data: MatchResultCreate,
    current_user: User = Depends(get_current_active_user)
):
    """매치 결과 등록 - 클럽 매니저만 가능"""
    match = await Match.get_or_none(
        id=match_id, is_deleted=False
    ).prefetch_related("session__event__club")
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="매치를 찾을 수 없습니다"
        )

    await verify_club_manager(match.session, current_user)

    # 이미 결과가 있는지 확인
    existing_result = await MatchResult.get_or_none(match_id=match_id)
    if existing_result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 결과가 있습니다"
        )

    # 점수 검증
    if result_data.team_a_score < 0 or result_data.team_b_score < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="점수는 0 이상이어야 합니다"
        )

    result = await MatchResult.create(
        match_id=match_id,
        team_a_score=result_data.team_a_score,
        team_b_score=result_data.team_b_score,
        sets_detail=result_data.sets_detail,
        winner_team=result_data.winner_team,
        recorded_by=current_user
    )

    return MatchResultResponse.model_validate(result)


@router.get("/{match_id}/result", response_model=MatchResultResponse)
async def get_match_result(
    match_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """매치 결과 조회 - 클럽 멤버만 가능"""
    match = await Match.get_or_none(
        id=match_id, is_deleted=False
    ).prefetch_related("session__event__club")
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="매치를 찾을 수 없습니다"
        )

    await verify_club_member(match.session, current_user)

    result = await MatchResult.get_or_none(match_id=match_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="매치 결과를 찾을 수 없습니다"
        )
    return MatchResultResponse.model_validate(result)
