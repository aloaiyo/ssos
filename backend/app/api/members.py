"""
회원 관리 API

권한 체계:
- 회원 목록 조회: 매니저/일반회원만 가능 (게스트 제외)
- 회원 역할 변경: 매니저만 가능
- 회원 승인/내보내기: 매니저만 가능
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from app.models.member import ClubMember, MemberRole, MemberStatus
from app.core.dependencies import (
    require_club_member_not_guest,
    require_club_manager,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/clubs/{club_id}/members", tags=["회원 관리"])


# ============ Request/Response Schemas ============

class MemberRoleUpdate(BaseModel):
    """회원 역할 변경 요청"""
    role: str  # manager, member, guest


class MemberResponse(BaseModel):
    """회원 응답"""
    id: int
    user_id: int
    user_name: str
    user_email: str
    gender: str
    role: str
    status: str
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class MemberListResponse(BaseModel):
    """회원 목록 응답"""
    members: List[MemberResponse]
    total: int


# ============ API Endpoints ============

@router.get("", response_model=List[MemberResponse])
async def list_members(
    club_id: int,
    status_filter: Optional[str] = None,
    membership: ClubMember = Depends(require_club_member_not_guest)
) -> List[MemberResponse]:
    """
    회원 목록 조회

    - 게스트는 조회 불가 (403)
    - 매니저/일반회원만 조회 가능
    """
    try:
        query = ClubMember.filter(club_id=club_id, is_deleted=False).prefetch_related("user")

        if status_filter:
            # 유효한 상태값인지 확인
            valid_statuses = [s.value for s in MemberStatus]
            if status_filter not in valid_statuses:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"유효하지 않은 상태입니다. 가능한 값: {', '.join(valid_statuses)}"
                )
            query = query.filter(status=status_filter)

        members = await query

        return [MemberResponse(
            id=m.id,
            user_id=m.user_id,
            user_name=m.user.name or (m.user.email.split('@')[0] if m.user.email else '회원'),
            user_email=m.user.email or '',
            gender=m.gender.value,
            role=m.role.value,
            status=m.status.value,
            created_at=m.created_at.isoformat(),
        ) for m in members]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"회원 목록 조회 실패: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="회원 목록을 불러오는 중 오류가 발생했습니다"
        )


@router.post("/{member_id}/approve")
async def approve_member(
    club_id: int,
    member_id: int,
    manager: ClubMember = Depends(require_club_manager)
):
    """회원 가입 승인 (매니저만)"""
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
    role_data: MemberRoleUpdate,
    manager: ClubMember = Depends(require_club_manager)
):
    """
    회원 역할 변경 (매니저만)

    - 역할: manager(매니저), member(일반회원), guest(게스트)
    - 매니저 → 다른 역할: 최소 1명의 매니저 필요
    """
    member = await ClubMember.get_or_none(id=member_id, club_id=club_id, is_deleted=False)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="회원을 찾을 수 없습니다"
        )

    # 유효한 역할인지 확인
    valid_roles = [r.value for r in MemberRole]
    if role_data.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"유효하지 않은 역할입니다. 가능한 값: {', '.join(valid_roles)}"
        )

    new_role = role_data.role

    # 매니저를 다른 역할로 변경하려는 경우, 최소 1명의 매니저가 남아있는지 확인
    if member.role == MemberRole.MANAGER and new_role != MemberRole.MANAGER.value:
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

    return {"message": "역할이 변경되었습니다", "new_role": new_role}


@router.delete("/{member_id}")
async def remove_member(
    club_id: int,
    member_id: int,
    manager: ClubMember = Depends(require_club_manager)
):
    """회원 내보내기 (매니저만, soft delete)"""
    member = await ClubMember.get_or_none(id=member_id, club_id=club_id, is_deleted=False)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="회원을 찾을 수 없습니다"
        )

    # 자기 자신을 내보낼 수 없음
    if member.id == manager.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="자기 자신을 내보낼 수 없습니다"
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
