"""
사용자 관련 API
"""
from fastapi import APIRouter, Depends
from app.models.user import User
from app.core.dependencies import get_current_active_user
from app.models.member import ClubMember, MemberStatus
from app.core.timezone import serialize_to_kst

router = APIRouter(prefix="/users", tags=["사용자"])


@router.get("/me/clubs")
async def get_my_clubs(current_user: User = Depends(get_current_active_user)):
    """현재 사용자가 가입한 동호회 목록"""
    memberships = await ClubMember.filter(
        user=current_user,
        status=MemberStatus.ACTIVE,
        is_deleted=False
    ).prefetch_related("club")

    # 삭제된 동호회 제외
    return [{
        "id": m.club.id,
        "name": m.club.name,
        "description": m.club.description,
        "my_role": m.role.value,
        "member_count": await ClubMember.filter(club=m.club, status=MemberStatus.ACTIVE, is_deleted=False).count(),
        "created_at": serialize_to_kst(m.club.created_at),
    } for m in memberships if not m.club.is_deleted]
