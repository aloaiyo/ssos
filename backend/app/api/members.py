"""
동호회 회원 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.member import ClubMemberCreate, ClubMemberResponse, ClubMemberDetailResponse, ClubMemberUpdate
from app.models.club import Club
from app.models.member import ClubMember, MemberRole
from app.models.user import User
from app.core.dependencies import get_current_active_user

router = APIRouter(prefix="/clubs/{club_id}/members", tags=["동호회 회원"])


@router.get("", response_model=List[ClubMemberDetailResponse])
async def list_club_members(
    club_id: int,
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100
):
    """동호회 회원 목록 조회"""
    club = await Club.get_or_none(id=club_id)
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="동호회를 찾을 수 없습니다"
        )

    members = await ClubMember.filter(club_id=club_id).prefetch_related('user').offset(skip).limit(limit)

    return [
        ClubMemberDetailResponse(
            id=member.id,
            club_id=member.club_id,
            user_id=member.user_id,
            role=member.role,
            gender=member.gender,
            preferred_type=member.preferred_type,
            joined_at=member.joined_at,
            user_name=member.user.name,
            user_email=member.user.email
        )
        for member in members
    ]


@router.post("", response_model=ClubMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_club_member(
    club_id: int,
    member_data: ClubMemberCreate,
    current_user: User = Depends(get_current_active_user)
):
    """동호회 회원 추가"""
    club = await Club.get_or_none(id=club_id)
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="동호회를 찾을 수 없습니다"
        )

    # 사용자 존재 확인
    user = await User.get_or_none(id=member_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )

    # 중복 확인
    existing_member = await ClubMember.get_or_none(club_id=club_id, user_id=member_data.user_id)
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 동호회 회원입니다"
        )

    # 회원 추가
    member = await ClubMember.create(
        club_id=club_id,
        user_id=member_data.user_id,
        gender=member_data.gender,
        preferred_type=member_data.preferred_type
    )

    return ClubMemberResponse.model_validate(member)


@router.get("/{member_id}", response_model=ClubMemberDetailResponse)
async def get_club_member(
    club_id: int,
    member_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """동호회 회원 상세 조회"""
    member = await ClubMember.get_or_none(id=member_id, club_id=club_id).prefetch_related('user')
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="회원을 찾을 수 없습니다"
        )

    return ClubMemberDetailResponse(
        id=member.id,
        club_id=member.club_id,
        user_id=member.user_id,
        role=member.role,
        gender=member.gender,
        preferred_type=member.preferred_type,
        joined_at=member.joined_at,
        user_name=member.user.name,
        user_email=member.user.email
    )


@router.put("/{member_id}", response_model=ClubMemberResponse)
async def update_club_member(
    club_id: int,
    member_id: int,
    member_data: ClubMemberUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """동호회 회원 정보 수정"""
    member = await ClubMember.get_or_none(id=member_id, club_id=club_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="회원을 찾을 수 없습니다"
        )

    # 권한 확인 (관리자 또는 본인만 수정 가능)
    if member.user_id != current_user.id:
        # 관리자 권한 확인
        admin_member = await ClubMember.get_or_none(club_id=club_id, user_id=current_user.id)
        if not admin_member or (admin_member.role != MemberRole.ADMIN and not current_user.is_super_admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="회원 정보를 수정할 권한이 없습니다"
            )

    # 수정
    if member_data.role is not None:
        member.role = member_data.role
    if member_data.gender is not None:
        member.gender = member_data.gender
    if member_data.preferred_type is not None:
        member.preferred_type = member_data.preferred_type

    await member.save()
    return ClubMemberResponse.model_validate(member)


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_club_member(
    club_id: int,
    member_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """동호회 회원 제거"""
    member = await ClubMember.get_or_none(id=member_id, club_id=club_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="회원을 찾을 수 없습니다"
        )

    # 권한 확인 (관리자 또는 본인만 제거 가능)
    if member.user_id != current_user.id:
        admin_member = await ClubMember.get_or_none(club_id=club_id, user_id=current_user.id)
        if not admin_member or (admin_member.role != MemberRole.ADMIN and not current_user.is_super_admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="회원을 제거할 권한이 없습니다"
            )

    await member.delete()
