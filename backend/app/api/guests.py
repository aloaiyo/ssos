"""
게스트 관리 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel as PydanticBase
from app.models.club import Club
from app.models.guest import Guest
from app.models.member import ClubMember, MemberRole, MemberStatus, Gender
from app.models.user import User
from app.core.dependencies import get_current_active_user

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


async def check_member_permission(club_id: int, current_user: User):
    """회원 권한 확인 (매니저 또는 일반 회원)"""
    club = await Club.get_or_none(id=club_id, is_deleted=False)
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="동호회를 찾을 수 없습니다"
        )

    member = await ClubMember.get_or_none(club_id=club_id, user=current_user, is_deleted=False)
    if not member or member.status != MemberStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없습니다"
        )
    return club, member


async def check_manager_permission(club_id: int, current_user: User):
    """매니저 권한 확인"""
    club = await Club.get_or_none(id=club_id, is_deleted=False)
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="동호회를 찾을 수 없습니다"
        )

    member = await ClubMember.get_or_none(club_id=club_id, user=current_user, is_deleted=False)
    if not member or member.role != MemberRole.MANAGER or member.status != MemberStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없습니다"
        )
    return club


@router.get("")
async def list_guests(
    club_id: int,
    current_user: User = Depends(get_current_active_user)
) -> List[GuestResponse]:
    """게스트 목록 조회"""
    await check_member_permission(club_id, current_user)

    guests = await Guest.filter(club_id=club_id)

    return [GuestResponse(
        id=g.id,
        name=g.name,
        gender=g.gender.value,
        phone=g.phone,
        notes=g.notes,
        total_games=g.total_games,
        wins=g.wins,
        losses=g.losses,
        draws=g.draws,
        win_rate=g.win_rate
    ) for g in guests]


@router.post("")
async def create_guest(
    club_id: int,
    guest_data: GuestCreate,
    current_user: User = Depends(get_current_active_user)
):
    """게스트 생성"""
    await check_manager_permission(club_id, current_user)

    guest = await Guest.create(
        club_id=club_id,
        name=guest_data.name,
        gender=Gender(guest_data.gender),
        phone=guest_data.phone,
        notes=guest_data.notes
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
    current_user: User = Depends(get_current_active_user)
) -> GuestResponse:
    """게스트 상세 조회"""
    await check_member_permission(club_id, current_user)

    guest = await Guest.get_or_none(id=guest_id, club_id=club_id)
    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게스트를 찾을 수 없습니다"
        )

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
        win_rate=guest.win_rate
    )


@router.put("/{guest_id}")
async def update_guest(
    club_id: int,
    guest_id: int,
    guest_data: GuestUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """게스트 정보 수정"""
    await check_manager_permission(club_id, current_user)

    guest = await Guest.get_or_none(id=guest_id, club_id=club_id)
    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게스트를 찾을 수 없습니다"
        )

    if guest_data.name is not None:
        guest.name = guest_data.name
    if guest_data.gender is not None:
        guest.gender = Gender(guest_data.gender)
    if guest_data.phone is not None:
        guest.phone = guest_data.phone
    if guest_data.notes is not None:
        guest.notes = guest_data.notes

    await guest.save()

    return {"message": "게스트 정보가 수정되었습니다"}


@router.delete("/{guest_id}")
async def delete_guest(
    club_id: int,
    guest_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """게스트 삭제"""
    await check_manager_permission(club_id, current_user)

    guest = await Guest.get_or_none(id=guest_id, club_id=club_id)
    if not guest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게스트를 찾을 수 없습니다"
        )

    # 경기 기록이 있는 경우 삭제 불가
    if guest.total_games > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="경기 기록이 있는 게스트는 삭제할 수 없습니다"
        )

    await guest.delete()

    return {"message": "게스트가 삭제되었습니다"}
