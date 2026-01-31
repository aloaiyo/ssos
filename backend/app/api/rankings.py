"""
랭킹 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.ranking import RankingResponse, RankingDetailResponse
from app.models.ranking import Ranking
from app.models.club import Club
from app.models.user import User
from app.core.dependencies import get_current_active_user, get_club_or_404

router = APIRouter(tags=["랭킹"])


@router.get("/clubs/{club_id}/rankings", response_model=List[RankingDetailResponse])
async def list_rankings(
    club_id: int,
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100
):
    """동호회 랭킹 목록 조회"""
    await get_club_or_404(club_id)

    rankings = await Ranking.filter(club_id=club_id).prefetch_related(
        'club_member__user'
    ).order_by('-points', '-wins', 'losses').offset(skip).limit(limit)

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
            member_name=ranking.club_member.user.name if ranking.club_member and ranking.club_member.user else "Unknown",
            member_email=ranking.club_member.user.email if ranking.club_member and ranking.club_member.user else ""
        )
        for ranking in rankings
    ]


@router.get("/clubs/{club_id}/rankings/{member_id}", response_model=RankingDetailResponse)
async def get_member_ranking(
    club_id: int,
    member_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """회원 랭킹 상세 조회"""
    await get_club_or_404(club_id)

    ranking = await Ranking.get_or_none(
        club_id=club_id, club_member_id=member_id
    ).prefetch_related('club_member__user')

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
        member_name=ranking.club_member.user.name if ranking.club_member and ranking.club_member.user else "Unknown",
        member_email=ranking.club_member.user.email if ranking.club_member and ranking.club_member.user else ""
    )


@router.post("/clubs/{club_id}/rankings/update")
async def update_rankings(
    club_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """동호회 랭킹 갱신 (전체 경기 결과 기반)"""
    from app.models.match import Match, MatchResult, MatchParticipant, Team, MatchStatus
    from app.models.member import ClubMember
    from collections import defaultdict
    from tortoise.transactions import in_transaction

    await get_club_or_404(club_id)

    # 클럽의 모든 완료된 경기 조회
    matches = await Match.filter(
        session__event__club_id=club_id,
        status=MatchStatus.COMPLETED,
        is_deleted=False
    ).prefetch_related("participants__club_member")

    # 통계 집계
    stats = defaultdict(lambda: {"wins": 0, "draws": 0, "losses": 0, "total": 0})

    for match in matches:
        result = await MatchResult.get_or_none(match=match)
        if not result:
            continue

        participants = await MatchParticipant.filter(match=match).prefetch_related("club_member")

        team_a_members = [p.club_member_id for p in participants if p.team == Team.A and p.club_member_id]
        team_b_members = [p.club_member_id for p in participants if p.team == Team.B and p.club_member_id]

        if result.winner_team == Team.A:
            for member_id in team_a_members:
                stats[member_id]["wins"] += 1
                stats[member_id]["total"] += 1
            for member_id in team_b_members:
                stats[member_id]["losses"] += 1
                stats[member_id]["total"] += 1
        elif result.winner_team == Team.B:
            for member_id in team_b_members:
                stats[member_id]["wins"] += 1
                stats[member_id]["total"] += 1
            for member_id in team_a_members:
                stats[member_id]["losses"] += 1
                stats[member_id]["total"] += 1
        else:
            for member_id in team_a_members + team_b_members:
                stats[member_id]["draws"] += 1
                stats[member_id]["total"] += 1

    # 랭킹 업데이트
    async with in_transaction():
        for member_id, stat in stats.items():
            ranking, created = await Ranking.get_or_create(
                club_id=club_id,
                club_member_id=member_id,
                defaults={
                    "total_matches": stat["total"],
                    "wins": stat["wins"],
                    "draws": stat["draws"],
                    "losses": stat["losses"],
                    "points": stat["wins"] * 3 + stat["draws"]
                }
            )
            if not created:
                ranking.total_matches = stat["total"]
                ranking.wins = stat["wins"]
                ranking.draws = stat["draws"]
                ranking.losses = stat["losses"]
                ranking.points = stat["wins"] * 3 + stat["draws"]
                await ranking.save()

    return {"message": "랭킹이 갱신되었습니다", "updated_members": len(stats)}
