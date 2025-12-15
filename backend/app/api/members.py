"""
회원 관리 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.club import Club
from app.models.member import ClubMember, MemberRole, MemberStatus
from app.models.user import User
from app.core.dependencies import get_current_active_user

router = APIRouter(prefix="/clubs/{club_id}/members", tags=["회원 관리"])


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
async def list_members(
    club_id: int,
    status_filter: str = None,
    current_user: User = Depends(get_current_active_user)
):
    """회원 목록 조회"""
    club = await Club.get_or_none(id=club_id, is_deleted=False)
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="동호회를 찾을 수 없습니다"
        )

    try:
        query = ClubMember.filter(club=club, is_deleted=False).prefetch_related("user")

        if status_filter:
            query = query.filter(status=status_filter)

        members = await query
        
        return [{
            "id": m.id,
            "user_id": m.user_id,
            "user_name": m.user.name,
            "user_email": m.user.email,
            "gender": m.gender.value,
            "role": m.role.value,
            "status": m.status.value,
            "created_at": m.created_at.isoformat(),
        } for m in members]
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"회원 목록 조회 실패: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"회원 목록을 불러오는 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/{member_id}/approve")
async def approve_member(
    club_id: int,
    member_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """회원 가입 승인"""
    await check_manager_permission(club_id, current_user)

    member = await ClubMember.get_or_none(id=member_id, club_id=club_id, is_deleted=False)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="회원을 찾을 수 없습니다"
        )

    if member.status != MemberStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="승인 대기 중인 회원이 아닙니다"
        )

    member.status = MemberStatus.ACTIVE
    await member.save()

    return {"message": "회원 가입을 승인했습니다"}


@router.put("/{member_id}")
async def update_member_role(
    club_id: int,
    member_id: int,
    role_data: dict,
    current_user: User = Depends(get_current_active_user)
):
    """회원 역할 변경"""
    await check_manager_permission(club_id, current_user)

    member = await ClubMember.get_or_none(id=member_id, club_id=club_id, is_deleted=False)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="회원을 찾을 수 없습니다"
        )

    new_role = role_data.get("role")
    if new_role not in [MemberRole.MANAGER.value, MemberRole.MEMBER.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유효하지 않은 역할입니다"
        )

    # 매니저를 멤버로 변경하려는 경우, 최소 1명의 매니저가 남아있는지 확인
    if member.role == MemberRole.MANAGER and new_role == MemberRole.MEMBER.value:
        manager_count = await ClubMember.filter(
            club_id=club_id,
            role=MemberRole.MANAGER,
            status=MemberStatus.ACTIVE,
            is_deleted=False
        ).count()

        if manager_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="최소 1명의 매니저가 필요합니다"
            )

    member.role = MemberRole(new_role)
    await member.save()

    return {"message": "역할이 변경되었습니다"}


@router.delete("/{member_id}")
async def remove_member(
    club_id: int,
    member_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """회원 내보내기 (soft delete)"""
    await check_manager_permission(club_id, current_user)

    member = await ClubMember.get_or_none(id=member_id, club_id=club_id, is_deleted=False)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="회원을 찾을 수 없습니다"
        )

    # 매니저를 내보내려는 경우, 최소 1명의 매니저가 남아있는지 확인
    if member.role == MemberRole.MANAGER:
        manager_count = await ClubMember.filter(
            club_id=club_id,
            role=MemberRole.MANAGER,
            status=MemberStatus.ACTIVE,
            is_deleted=False
        ).count()

        if manager_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="최소 1명의 매니저가 필요합니다. 다른 회원을 매니저로 지정한 후 진행해주세요."
            )

    # Soft delete
    member.is_deleted = True
    await member.save()

    return {"message": "회원을 내보냈습니다"}
