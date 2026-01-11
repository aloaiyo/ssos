"""
랭킹 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.ranking import RankingResponse, RankingDetailResponse
from app.models.ranking import Ranking
from app.models.club import Club
from app.models.user import User
from app.core.dependencies import get_current_active_user

router = APIRouter(prefix="/rankings", tags=["랭킹"])


@router.get("", response_model=List[RankingDetailResponse])
async def list_rankings(
    club_id: int,
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100
):
    """동호회 랭킹 목록 조회"""
    club = await Club.get_or_none(id=club_id, is_deleted=False)
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="동호회를 찾을 수 없습니다"
        )

    rankings = await Ranking.filter(club_id=club_id).prefetch_related(
        'club_member__user'
    ).offset(skip).limit(limit)

    return [
        RankingDetailResponse(
            id=ranking.id,
            club_id=ranking.club_id,
            club_member_id=ranking.club_member_id,
            total_matches=ranking.total_matches,
            wins=ranking.wins,
            draws=ranking.draws,
            losses=ranking.losses,
            points=ranking.points,
            last_updated=ranking.last_updated,
            win_rate=ranking.win_rate,
            member_name=ranking.club_member.user.name,
            member_email=ranking.club_member.user.email
        )
        for ranking in rankings
    ]


@router.get("/{ranking_id}", response_model=RankingDetailResponse)
async def get_ranking(
    ranking_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """랭킹 상세 조회"""
    ranking = await Ranking.get_or_none(id=ranking_id).prefetch_related('club_member__user')
    if not ranking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="랭킹 정보를 찾을 수 없습니다"
        )

    return RankingDetailResponse(
        id=ranking.id,
        club_id=ranking.club_id,
        club_member_id=ranking.club_member_id,
        total_matches=ranking.total_matches,
        wins=ranking.wins,
        draws=ranking.draws,
        losses=ranking.losses,
        points=ranking.points,
        last_updated=ranking.last_updated,
        win_rate=ranking.win_rate,
        member_name=ranking.club_member.user.name,
        member_email=ranking.club_member.user.email
    )
