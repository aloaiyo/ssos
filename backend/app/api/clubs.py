"""
동호회 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.club import ClubCreate, ClubResponse, ClubUpdate
from app.models.club import Club
from app.models.user import User
from app.core.dependencies import get_current_active_user

router = APIRouter(prefix="/clubs", tags=["동호회"])


@router.get("", response_model=List[ClubResponse])
async def list_clubs(
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100
):
    """동호회 목록 조회"""
    clubs = await Club.all().offset(skip).limit(limit)
    return [ClubResponse.model_validate(club) for club in clubs]


@router.post("", response_model=ClubResponse, status_code=status.HTTP_201_CREATED)
async def create_club(
    club_data: ClubCreate,
    current_user: User = Depends(get_current_active_user)
):
    """동호회 생성"""
    club = await Club.create(
        name=club_data.name,
        description=club_data.description,
        created_by=current_user
    )
    return ClubResponse.model_validate(club)


@router.get("/{club_id}", response_model=ClubResponse)
async def get_club(
    club_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """동호회 상세 조회"""
    club = await Club.get_or_none(id=club_id)
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="동호회를 찾을 수 없습니다"
        )
    return ClubResponse.model_validate(club)


@router.put("/{club_id}", response_model=ClubResponse)
async def update_club(
    club_id: int,
    club_data: ClubUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """동호회 수정"""
    club = await Club.get_or_none(id=club_id)
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="동호회를 찾을 수 없습니다"
        )

    # 권한 확인 (생성자만 수정 가능)
    if club.created_by_id != current_user.id and not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="동호회를 수정할 권한이 없습니다"
        )

    # 수정
    if club_data.name is not None:
        club.name = club_data.name
    if club_data.description is not None:
        club.description = club_data.description

    await club.save()
    return ClubResponse.model_validate(club)


@router.delete("/{club_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_club(
    club_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """동호회 삭제"""
    club = await Club.get_or_none(id=club_id)
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="동호회를 찾을 수 없습니다"
        )

    # 권한 확인
    if club.created_by_id != current_user.id and not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="동호회를 삭제할 권한이 없습니다"
        )

    await club.delete()
