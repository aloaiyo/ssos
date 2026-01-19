"""
게스트 관리 API

게스트 유형:
1. 미가입 게스트: 매니저가 생성, User 계정 없음
2. 가입 게스트: 서비스 가입 후 동호회에 게스트로 참여 (ClubMember role=GUEST)

이 API는 미가입 게스트(Guest 모델)를 관리합니다.
가입 게스트는 회원 API(members.py)에서 role=GUEST로 관리됩니다.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel as PydanticBase
from tortoise.transactions import in_transaction
from app.models.club import Club
from app.models.guest import Guest
from app.models.member import ClubMember, MemberRole, MemberStatus, Gender
from app.models.user import User
from app.models.match import MatchParticipant, ParticipantCategory
from app.models.event import SessionParticipant
from app.core.dependencies import (
    get_current_active_user,
    require_club_manager,
    require_club_member_not_guest,
)

router = APIRouter(prefix="/clubs/{club_id}/guests", tags=["게스트 관리"])


class GuestCreate(PydanticBase):
    name: str
    gender: str  # male, female
    phone: Optional[str] = None
    notes: Optional[str] = None


class GuestUpdate(PydanticBase):
    name: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None


class GuestLinkRequest(PydanticBase):
    """게스트-회원 연결 요청"""
    member_id: int
    transfer_records: bool = True  # 경기 기록 이전 여부


class GuestResponse(PydanticBase):
    id: int
    name: str
    gender: str
    phone: Optional[str]
    notes: Optional[str]
    total_games: int
    wins: int
    losses: int
    draws: int
    win_rate: float
    # 연결 정보
    is_linked: bool = False
    linked_member_id: Optional[int] = None
    linked_member_name: Optional[str] = None
    created_by_id: Optional[int] = None
    created_by_name: Optional[str] = None


async def _build_guest_response(guest: Guest) -> GuestResponse:
    """게스트 응답 객체 생성"""
    linked_member_name = None
    created_by_name = None

    if guest.linked_member_id:
        linked_member = await ClubMember.get_or_none(id=guest.linked_member_id).prefetch_related("user")
        if linked_member:
            linked_member_name = linked_member.user.name or linked_member.nickname

    if guest.created_by_id:
        created_by = await ClubMember.get_or_none(id=guest.created_by_id).prefetch_related("user")
        if created_by:
            created_by_name = created_by.user.name or created_by.nickname

    return GuestResponse(
        id=guest.id,
        name=guest.name,
        gender=guest.gender.value,
        phone=guest.phone,
        notes=guest.notes,
        total_games=guest.total_games,
        wins=guest.wins,
        losses=guest.losses,
        draws=guest.draws,
        win_rate=guest.win_rate,
        is_linked=guest.linked_member_id is not None,
        linked_member_id=guest.linked_member_id,
        linked_member_name=linked_member_name,
        created_by_id=guest.created_by_id,
        created_by_name=created_by_name,
    )


@router.get("")
async def list_guests(
    club_id: int,
    include_linked: bool = True,
    membership: ClubMember = Depends(require_club_member_not_guest)
) -> List[GuestResponse]:
    """
    게스트 목록 조회

    - 게스트는 조회 불가 (403)
    - include_linked=False: 연결되지 않은 게스트만 조회
    """
    query = Guest.filter(club_id=club_id, is_deleted=False)

    if not include_linked:
        query = query.filter(linked_member_id=None)

    guests = await query

    return [await _build_guest_response(g) for g in guests]


@router.post("")
async def create_guest(
    club_id: int,
    guest_data: GuestCreate,
    membership: ClubMember = Depends(require_club_manager)
):
    """
    게스트 생성 (매니저만)

    - 미가입 참가자를 게스트로 등록
    - 나중에 해당 참가자가 서비스에 가입하면 연결 가능
    """
    # 성별 유효성 검사
    valid_genders = [g.value for g in Gender]
    if guest_data.gender not in valid_genders:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"유효하지 않은 성별입니다. 가능한 값: {', '.join(valid_genders)}"
        )

    guest = await Guest.create(
        club_id=club_id,
        name=guest_data.name,
        gender=Gender(guest_data.gender),
        phone=guest_data.phone,
        notes=guest_data.notes,
        created_by=membership,  # 생성한 매니저 기록
    )

    return {
        "id": guest.id,
        "name": guest.name,
        "gender": guest.gender.value,
        "message": "게스트가 등록되었습니다"
    }


@router.get("/{guest_id}")
async def get_guest(
    club_id: int,
    guest_id: int,
    membership: ClubMember = Depends(require_club_member_not_guest)
) -> GuestResponse:
    """게스트 상세 조회"""
    guest = await Guest.get_or_none(id=guest_id, club_id=club_id, is_deleted=False)
    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게스트를 찾을 수 없습니다"
        )

    return await _build_guest_response(guest)


@router.put("/{guest_id}")
async def update_guest(
    club_id: int,
    guest_id: int,
    guest_data: GuestUpdate,
    membership: ClubMember = Depends(require_club_manager)
):
    """게스트 정보 수정 (매니저만)"""
    guest = await Guest.get_or_none(id=guest_id, club_id=club_id, is_deleted=False)
    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게스트를 찾을 수 없습니다"
        )

    if guest_data.name is not None:
        guest.name = guest_data.name
    if guest_data.gender is not None:
        # 성별 유효성 검사
        valid_genders = [g.value for g in Gender]
        if guest_data.gender not in valid_genders:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"유효하지 않은 성별입니다. 가능한 값: {', '.join(valid_genders)}"
            )
        guest.gender = Gender(guest_data.gender)
    if guest_data.phone is not None:
        guest.phone = guest_data.phone
    if guest_data.notes is not None:
        guest.notes = guest_data.notes

    await guest.save()

    return {"message": "게스트 정보가 수정되었습니다"}


@router.post("/{guest_id}/link")
async def link_guest_to_member(
    club_id: int,
    guest_id: int,
    link_data: GuestLinkRequest,
    membership: ClubMember = Depends(require_club_manager)
):
    """
    게스트를 회원과 연결 (매니저만)

    - 미가입 게스트가 서비스에 가입한 후 기존 기록과 연결
    - transfer_records=True: 경기 기록을 회원에게 이전
    """
    guest = await Guest.get_or_none(id=guest_id, club_id=club_id, is_deleted=False)
    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게스트를 찾을 수 없습니다"
        )

    if guest.linked_member_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 다른 회원과 연결된 게스트입니다"
        )

    # 연결할 회원 확인
    target_member = await ClubMember.get_or_none(
        id=link_data.member_id,
        club_id=club_id,
        is_deleted=False
    )
    if not target_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="연결할 회원을 찾을 수 없습니다"
        )

    # 해당 회원이 이미 다른 게스트와 연결되어 있는지 확인 (같은 동호회 내에서)
    existing_link = await Guest.get_or_none(
        linked_member_id=link_data.member_id,
        club_id=club_id,
        is_deleted=False
    )
    if existing_link:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="해당 회원은 이미 다른 게스트와 연결되어 있습니다"
        )

    # 대상 회원이 활성 상태인지 확인
    if target_member.status != MemberStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="활성 상태인 회원만 연결할 수 있습니다"
        )

    async with in_transaction():
        # 게스트와 회원 연결
        guest.linked_member = target_member
        await guest.save()

        # 경기 기록 이전
        if link_data.transfer_records and guest.total_games > 0:
            target_member.total_games += guest.total_games
            target_member.wins += guest.wins
            target_member.losses += guest.losses
            target_member.draws += guest.draws
            await target_member.save()

            # MatchParticipant 참조 업데이트: guest → club_member
            match_participants = await MatchParticipant.filter(
                guest_id=guest.id,
                is_deleted=False
            )
            for mp in match_participants:
                mp.guest = None
                mp.club_member = target_member
                mp.participant_category = ParticipantCategory.MEMBER
                await mp.save()

            # SessionParticipant 참조 업데이트: guest → club_member
            session_participants = await SessionParticipant.filter(
                guest_id=guest.id,
                is_deleted=False
            )
            for sp in session_participants:
                sp.guest = None
                sp.club_member = target_member
                await sp.save()

    return {
        "message": "게스트가 회원과 연결되었습니다",
        "guest_id": guest.id,
        "member_id": target_member.id,
        "records_transferred": link_data.transfer_records and guest.total_games > 0
    }


@router.delete("/{guest_id}/link")
async def unlink_guest_from_member(
    club_id: int,
    guest_id: int,
    membership: ClubMember = Depends(require_club_manager)
):
    """게스트-회원 연결 해제 (매니저만)"""
    guest = await Guest.get_or_none(id=guest_id, club_id=club_id, is_deleted=False)
    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게스트를 찾을 수 없습니다"
        )

    if not guest.linked_member_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="연결된 회원이 없습니다"
        )

    guest.linked_member = None
    await guest.save()

    return {"message": "게스트-회원 연결이 해제되었습니다"}


@router.delete("/{guest_id}")
async def delete_guest(
    club_id: int,
    guest_id: int,
    membership: ClubMember = Depends(require_club_manager)
):
    """게스트 삭제 (매니저만, soft delete)"""
    guest = await Guest.get_or_none(id=guest_id, club_id=club_id, is_deleted=False)
    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게스트를 찾을 수 없습니다"
        )

    # 경기 기록이 있는 경우 삭제 불가 (단, 연결된 경우는 허용)
    if guest.total_games > 0 and not guest.linked_member_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="경기 기록이 있는 게스트는 삭제할 수 없습니다. 회원과 연결한 후 삭제하세요."
        )

    # Soft delete
    guest.is_deleted = True
    await guest.save()

    return {"message": "게스트가 삭제되었습니다"}
