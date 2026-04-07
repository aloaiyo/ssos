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

    # 삭제된 동호회 제외, 활성 클럽 ID 수집
    active_memberships = [m for m in memberships if not m.club.is_deleted]
    club_ids = [m.club.id for m in active_memberships]

    # 배치 쿼리로 모든 클럽의 회원 수 일괄 조회 (N+1 방지)
    member_count_map = {}
    if club_ids:
        from tortoise.functions import Count
        from tortoise.queryset import Q
        from app.models.club import Club

        clubs_with_count = await Club.filter(id__in=club_ids).annotate(
            active_member_count=Count(
                "members",
                _filter=Q(members__status=MemberStatus.ACTIVE, members__is_deleted=False)
            )
        )
        member_count_map = {c.id: c.active_member_count for c in clubs_with_count}

    return [{
        "id": m.club.id,
        "name": m.club.name,
        "description": m.club.description,
        "my_role": m.role.value,
        "member_count": member_count_map.get(m.club.id, 0),
        "created_at": serialize_to_kst(m.club.created_at),
        # 동호회 기본 설정값
        "location": m.club.location,
        "default_num_courts": m.club.default_num_courts,
        "default_match_duration": m.club.default_match_duration,
        "default_break_duration": m.club.default_break_duration,
        "default_warmup_duration": m.club.default_warmup_duration,
    } for m in active_memberships]
