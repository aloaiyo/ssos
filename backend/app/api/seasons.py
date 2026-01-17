"""
시즌 관리 API
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import date
from pydantic import BaseModel as PydanticBase, Field
from tortoise.functions import Count
from app.models.club import Club
from app.models.season import Season, SeasonStatus, SeasonRanking
from app.models.event import Session
from app.models.match import Match
from app.models.member import ClubMember
from app.models.user import User
from app.core.dependencies import (
    get_current_active_user,
    require_club_manager,
    get_club_or_404
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/clubs/{club_id}/seasons", tags=["시즌 관리"])


class SeasonCreate(PydanticBase):
    """시즌 생성 요청"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    start_date: date
    end_date: date


class SeasonUpdate(PydanticBase):
    """시즌 수정 요청"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None


@router.get("")
async def list_seasons(
    club_id: int,
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """시즌 목록 조회 (N+1 쿼리 최적화)"""
    club = await get_club_or_404(club_id)

    # status_filter 유효성 검사
    if status_filter and status_filter not in [s.value for s in SeasonStatus]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"유효하지 않은 상태입니다. 가능한 값: {[s.value for s in SeasonStatus]}"
        )

    query = Season.filter(club=club, is_deleted=False)
    if status_filter:
        query = query.filter(status=status_filter)

    seasons = await query.order_by("-start_date")

    # 모든 시즌 ID 수집
    season_ids = [s.id for s in seasons]

    # 배치 쿼리로 세션 수 조회
    session_counts = {}
    if season_ids:
        sessions = await Session.filter(
            season_id__in=season_ids, is_deleted=False
        ).values("season_id")
        for s in sessions:
            session_counts[s["season_id"]] = session_counts.get(s["season_id"], 0) + 1

    # 배치 쿼리로 매치 수 조회
    match_counts = {}
    if season_ids:
        matches = await Match.filter(
            session__season_id__in=season_ids, is_deleted=False
        ).values("session__season_id")
        for m in matches:
            sid = m["session__season_id"]
            match_counts[sid] = match_counts.get(sid, 0) + 1

    result = []
    for season in seasons:
        result.append({
            "id": season.id,
            "name": season.name,
            "description": season.description,
            "start_date": season.start_date.isoformat(),
            "end_date": season.end_date.isoformat(),
            "status": season.status.value,
            "session_count": session_counts.get(season.id, 0),
            "match_count": match_counts.get(season.id, 0),
            "created_at": season.created_at.isoformat(),
        })

    return result


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_season(
    club_id: int,
    season_data: SeasonCreate,
    membership: ClubMember = Depends(require_club_manager)
):
    """시즌 생성"""
    # 날짜 유효성 검사
    if season_data.start_date >= season_data.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="시작일은 종료일보다 이전이어야 합니다"
        )

    # 시즌 상태 자동 결정
    today = date.today()
    if season_data.start_date > today:
        initial_status = SeasonStatus.UPCOMING
    elif season_data.end_date < today:
        initial_status = SeasonStatus.COMPLETED
    else:
        initial_status = SeasonStatus.ACTIVE

    season = await Season.create(
        club_id=club_id,
        name=season_data.name,
        description=season_data.description,
        start_date=season_data.start_date,
        end_date=season_data.end_date,
        status=initial_status
    )

    return {
        "id": season.id,
        "name": season.name,
        "description": season.description,
        "start_date": season.start_date.isoformat(),
        "end_date": season.end_date.isoformat(),
        "status": season.status.value,
        "created_at": season.created_at.isoformat(),
    }


async def get_season_or_404(season_id: int, club_id: int) -> Season:
    """시즌 조회 또는 404"""
    season = await Season.get_or_none(id=season_id, club_id=club_id, is_deleted=False)
    if not season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="시즌을 찾을 수 없습니다"
        )
    return season


@router.get("/{season_id}")
async def get_season(
    club_id: int,
    season_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """시즌 상세 조회 (N+1 쿼리 최적화)"""
    season = await get_season_or_404(season_id, club_id)

    # 세션 목록 조회 - prefetch 활용
    sessions = await Session.filter(
        season=season, is_deleted=False
    ).prefetch_related("participants").order_by("-date")

    session_ids = [s.id for s in sessions]

    # 배치 쿼리로 매치 수 조회
    match_counts = {}
    if session_ids:
        matches = await Match.filter(
            session_id__in=session_ids, is_deleted=False
        ).values("session_id")
        for m in matches:
            sid = m["session_id"]
            match_counts[sid] = match_counts.get(sid, 0) + 1

    session_list = []
    total_match_count = 0
    for s in sessions:
        session_match_count = match_counts.get(s.id, 0)
        total_match_count += session_match_count
        session_list.append({
            "id": s.id,
            "title": s.title,
            "date": s.date.isoformat(),
            "start_time": s.start_time.isoformat(),
            "end_time": s.end_time.isoformat(),
            "location": s.location,
            "session_type": s.session_type.value if s.session_type else "league",
            "status": s.status.value,
            "participant_count": len([p for p in s.participants if not p.is_deleted]),
            "match_count": session_match_count,
        })

    return {
        "id": season.id,
        "name": season.name,
        "description": season.description,
        "start_date": season.start_date.isoformat(),
        "end_date": season.end_date.isoformat(),
        "status": season.status.value,
        "session_count": len(sessions),
        "match_count": total_match_count,
        "sessions": session_list,
        "created_at": season.created_at.isoformat(),
    }


@router.put("/{season_id}")
async def update_season(
    club_id: int,
    season_id: int,
    season_data: SeasonUpdate,
    membership: ClubMember = Depends(require_club_manager)
):
    """시즌 수정"""
    season = await get_season_or_404(season_id, club_id)

    if season_data.name is not None:
        season.name = season_data.name
    if season_data.description is not None:
        season.description = season_data.description
    if season_data.start_date is not None:
        season.start_date = season_data.start_date
    if season_data.end_date is not None:
        season.end_date = season_data.end_date
    if season_data.status is not None:
        try:
            season.status = SeasonStatus(season_data.status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"유효하지 않은 상태입니다. 가능한 값: {[s.value for s in SeasonStatus]}"
            )

    # 날짜 유효성 검사
    if season.start_date >= season.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="시작일은 종료일보다 이전이어야 합니다"
        )

    await season.save()

    return {
        "id": season.id,
        "name": season.name,
        "description": season.description,
        "start_date": season.start_date.isoformat(),
        "end_date": season.end_date.isoformat(),
        "status": season.status.value,
        "created_at": season.created_at.isoformat(),
    }


@router.delete("/{season_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_season(
    club_id: int,
    season_id: int,
    membership: ClubMember = Depends(require_club_manager)
):
    """시즌 삭제 (soft delete)"""
    season = await get_season_or_404(season_id, club_id)
    season.is_deleted = True
    await season.save()


@router.get("/{season_id}/rankings")
async def get_season_rankings(
    club_id: int,
    season_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """시즌 랭킹 조회"""
    season = await get_season_or_404(season_id, club_id)

    rankings = await SeasonRanking.filter(
        season=season, is_deleted=False
    ).prefetch_related("club_member__user").order_by("-points", "-wins", "losses")

    result = []
    for idx, ranking in enumerate(rankings, 1):
        member_name = "Unknown"
        if ranking.club_member and ranking.club_member.user:
            member_name = ranking.club_member.user.name or "Unknown"

        result.append({
            "rank": idx,
            "member_id": ranking.club_member_id,
            "member_name": member_name,
            "total_matches": ranking.total_matches,
            "wins": ranking.wins,
            "draws": ranking.draws,
            "losses": ranking.losses,
            "points": ranking.points,
            "win_rate": ranking.win_rate,
        })

    return {
        "season": {
            "id": season.id,
            "name": season.name,
            "status": season.status.value,
        },
        "rankings": result
    }


@router.post("/{season_id}/rankings/calculate")
async def calculate_season_rankings(
    club_id: int,
    season_id: int,
    membership: ClubMember = Depends(require_club_manager)
):
    """시즌 랭킹 계산 (경기 결과 기반)"""
    from tortoise.transactions import in_transaction
    from app.models.match import MatchResult, MatchParticipant, Team
    from collections import defaultdict

    season = await get_season_or_404(season_id, club_id)

    # 경기 결과 집계
    stats = defaultdict(lambda: {"wins": 0, "draws": 0, "losses": 0, "total": 0})
    errors = []

    matches = await Match.filter(
        session__season=season,
        status="completed",
        is_deleted=False
    ).prefetch_related("participants__club_member")

    for match in matches:
        try:
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
                # 무승부
                for member_id in team_a_members + team_b_members:
                    stats[member_id]["draws"] += 1
                    stats[member_id]["total"] += 1
        except Exception as e:
            logger.warning(f"Match {match.id} ranking calculation failed: {e}")
            errors.append(f"경기 {match.id} 처리 실패")
            continue

    # 트랜잭션 내에서 랭킹 업데이트 (원자적 처리)
    async with in_transaction():
        for member_id, stat in stats.items():
            ranking, created = await SeasonRanking.get_or_create(
                season=season,
                club_member_id=member_id,
                defaults={
                    "total_matches": stat["total"],
                    "wins": stat["wins"],
                    "draws": stat["draws"],
                    "losses": stat["losses"],
                    "points": stat["wins"] * 3 + stat["draws"]  # 승리 3점, 무승부 1점
                }
            )
            if not created:
                ranking.total_matches = stat["total"]
                ranking.wins = stat["wins"]
                ranking.draws = stat["draws"]
                ranking.losses = stat["losses"]
                ranking.points = stat["wins"] * 3 + stat["draws"]
                await ranking.save()

    response = {
        "message": "랭킹이 계산되었습니다",
        "total_members": len(stats),
        "total_matches_processed": len(matches)
    }

    if errors:
        response["warnings"] = errors[:10]  # 최대 10개만 반환

    return response
