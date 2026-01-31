"""
경기 결과지 OCR API
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List, Optional
from pydantic import BaseModel as PydanticBase, Field
from app.models.user import User
from app.models.club import Club
from app.models.season import Season
from app.models.event import Session, SessionParticipant, SessionStatus, SessionType, ParticipantCategory
from app.models.match import Match, MatchParticipant, MatchResult, MatchType, MatchStatus, Team
from app.models.member import ClubMember, MemberStatus
from app.core.dependencies import get_current_active_user, require_club_manager, get_club_or_404
from app.services.ocr_service import ocr_service
from datetime import date, time

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/clubs/{club_id}/ocr", tags=["OCR"])


class MatchPlayerData(PydanticBase):
    """경기 선수 데이터"""
    players: List[str]
    score: int


class ExtractedMatch(PydanticBase):
    """추출된 경기 데이터"""
    match_type: str
    court_number: int
    team_a: MatchPlayerData
    team_b: MatchPlayerData


class OCRResult(PydanticBase):
    """OCR 추출 결과"""
    date: Optional[str] = None
    location: Optional[str] = None
    matches: List[ExtractedMatch]


class PlayerMapping(PydanticBase):
    """선수 매핑 정보"""
    extracted_name: str
    member_id: Optional[int] = None
    guest_id: Optional[int] = None


class SaveMatchesRequest(PydanticBase):
    """경기 저장 요청"""
    # 시즌 관련
    season_id: Optional[int] = None
    create_new_season: bool = False
    new_season_name: Optional[str] = None
    new_season_start_date: Optional[date] = None
    new_season_end_date: Optional[date] = None
    new_season_description: Optional[str] = None

    # 세션 관련
    session_id: Optional[int] = None
    create_new_session: bool = False
    session_title: Optional[str] = None
    session_date: Optional[date] = None
    session_start_time: Optional[time] = Field(None, description="HH:MM:SS")
    session_end_time: Optional[time] = Field(None, description="HH:MM:SS")
    session_location: Optional[str] = None

    # 선수 매핑
    player_mappings: Optional[List[PlayerMapping]] = None

    # 경기 데이터
    matches: List[ExtractedMatch]


@router.post("/extract", response_model=OCRResult)
async def extract_match_results(
    club_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    경기 결과지 이미지에서 결과를 추출합니다.

    - 이미지 파일을 업로드하면 Gemini AI가 경기 결과를 추출합니다.
    - 지원 형식: JPEG, PNG, GIF, WebP
    """
    # 클럽 확인
    await get_club_or_404(club_id)

    # 파일 타입 확인
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"지원하지 않는 파일 형식입니다. 지원 형식: {', '.join(allowed_types)}"
        )

    # 파일 크기 확인 (10MB 제한)
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="파일 크기가 10MB를 초과합니다"
        )

    try:
        result = await ocr_service.extract_match_results(contents, file.content_type)
        return OCRResult(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"OCR 처리 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="이미지 처리 중 오류가 발생했습니다"
        )


@router.post("/save-matches")
async def save_extracted_matches(
    club_id: int,
    request: SaveMatchesRequest,
    membership: ClubMember = Depends(require_club_manager)
):
    """
    추출된 경기 결과를 저장합니다.

    - 기존 세션에 추가하거나 새 세션을 생성할 수 있습니다.
    - 새 시즌을 생성할 수 있습니다.
    - 선수 매핑 정보를 사용하거나 이름으로 회원을 매칭합니다.
    """
    from app.models.guest import Guest
    from app.models.season import SeasonStatus

    club = await get_club_or_404(club_id)

    # 시즌 결정
    season = None
    created_season_id = None

    if request.create_new_season:
        # 새 시즌 생성
        if not request.new_season_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="새 시즌 생성 시 이름은 필수입니다"
            )
        if not request.new_season_start_date or not request.new_season_end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="새 시즌 생성 시 시작일과 종료일은 필수입니다"
            )

        season = await Season.create(
            club_id=club_id,
            name=request.new_season_name,
            start_date=request.new_season_start_date,
            end_date=request.new_season_end_date,
            description=request.new_season_description or "",
            status=SeasonStatus.ACTIVE
        )
        created_season_id = season.id
        logger.info(f"새 시즌 생성: {season.name} (ID: {season.id})")

    elif request.season_id:
        # 기존 시즌 사용
        season = await Season.get_or_none(id=request.season_id, club_id=club_id, is_deleted=False)
        if not season:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="시즌을 찾을 수 없습니다"
            )

    # 세션 결정
    session = None
    if request.create_new_session:
        # 새 세션 생성
        if not request.session_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="새 세션 생성 시 날짜는 필수입니다"
            )

        from app.models.event import Event, EventType
        # 기본 이벤트 찾기 또는 생성
        event = None
        if not season:
            event = await Event.get_or_none(club_id=club_id, event_type=EventType.REGULAR)
            if not event:
                event = await Event.create(
                    club_id=club_id,
                    title="정기 모임",
                    event_type=EventType.REGULAR
                )

        session = await Session.create(
            event=event,
            season=season,
            title=request.session_title or f"경기 결과 ({request.session_date})",
            date=request.session_date,
            start_time=request.session_start_time or time(9, 0),
            end_time=request.session_end_time or time(12, 0),
            location=request.session_location or "",
            num_courts=4,
            session_type=SessionType.LEAGUE,
            status=SessionStatus.CONFIRMED
        )
    else:
        # 기존 세션 사용
        if not request.session_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="세션 ID가 필요합니다"
            )
        session = await Session.get_or_none(id=request.session_id, is_deleted=False)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="세션을 찾을 수 없습니다"
            )

    # 플레이어 매핑 딕셔너리 생성
    player_mapping_dict = {}
    if request.player_mappings:
        for mapping in request.player_mappings:
            player_mapping_dict[mapping.extracted_name] = mapping

    # 클럽 회원 목록 조회 (이름 매칭용, 매핑이 없는 경우 폴백)
    members = await ClubMember.filter(
        club_id=club_id,
        is_deleted=False,
        status=MemberStatus.ACTIVE
    ).prefetch_related("user")

    # ID -> 회원 매핑
    member_by_id = {member.id: member for member in members}

    # 게스트 목록 조회
    guests = await Guest.filter(club_id=club_id, is_deleted=False)
    guest_by_id = {guest.id: guest for guest in guests}

    # 이름 -> 회원 매핑 (폴백용)
    name_to_member = {}
    for member in members:
        if member.user:
            name = member.user.name
            if name:
                # 정규화된 이름으로 저장 (공백 제거, 소문자)
                normalized_name = name.replace(" ", "").lower()
                name_to_member[normalized_name] = member
                # 원본 이름도 저장
                name_to_member[name] = member

    def find_participant(player_name: str):
        """선수 이름으로 참가자 찾기 (회원 또는 게스트)"""
        if not player_name:
            return None, None

        # 1. 매핑 정보가 있으면 사용
        if player_name in player_mapping_dict:
            mapping = player_mapping_dict[player_name]
            if mapping.member_id and mapping.member_id in member_by_id:
                return member_by_id[mapping.member_id], None
            if mapping.guest_id and mapping.guest_id in guest_by_id:
                return None, guest_by_id[mapping.guest_id]

        # 2. 폴백: 이름으로 회원 찾기
        # 정확한 매칭
        if player_name in name_to_member:
            return name_to_member[player_name], None
        # 정규화된 이름으로 매칭
        normalized = player_name.replace(" ", "").lower()
        if normalized in name_to_member:
            return name_to_member[normalized], None
        # 부분 매칭
        for name, member in name_to_member.items():
            if player_name in name or name in player_name:
                return member, None

        return None, None

    created_matches = []
    unmatched_players = []

    for match_data in request.matches:
        # 매치 타입 변환
        match_type_map = {
            "mens_doubles": MatchType.MENS_DOUBLES,
            "mixed_doubles": MatchType.MIXED_DOUBLES,
            "singles": MatchType.SINGLES
        }
        match_type = match_type_map.get(match_data.match_type, MatchType.MENS_DOUBLES)

        # 경기 생성
        match_count = await Match.filter(session=session).count()
        match = await Match.create(
            session=session,
            match_number=match_count + 1,
            court_number=match_data.court_number,
            scheduled_time=session.start_time,
            match_type=match_type,
            status=MatchStatus.COMPLETED
        )

        # 팀 A 선수 추가
        for idx, player_name in enumerate(match_data.team_a.players, 1):
            member, guest = find_participant(player_name)
            if member:
                await MatchParticipant.create(
                    match=match,
                    club_member=member,
                    participant_category=ParticipantCategory.MEMBER,
                    team=Team.A,
                    position=idx
                )
                # 세션 참가자로도 추가
                existing = await SessionParticipant.get_or_none(session=session, club_member=member)
                if not existing:
                    await SessionParticipant.create(
                        session=session,
                        club_member=member,
                        participant_category=ParticipantCategory.MEMBER
                    )
            elif guest:
                await MatchParticipant.create(
                    match=match,
                    guest=guest,
                    participant_category=ParticipantCategory.GUEST,
                    team=Team.A,
                    position=idx
                )
                # 세션 참가자로도 추가
                existing = await SessionParticipant.get_or_none(session=session, guest=guest)
                if not existing:
                    await SessionParticipant.create(
                        session=session,
                        guest=guest,
                        participant_category=ParticipantCategory.GUEST
                    )
            else:
                unmatched_players.append(player_name)

        # 팀 B 선수 추가
        for idx, player_name in enumerate(match_data.team_b.players, 1):
            member, guest = find_participant(player_name)
            if member:
                await MatchParticipant.create(
                    match=match,
                    club_member=member,
                    participant_category=ParticipantCategory.MEMBER,
                    team=Team.B,
                    position=idx
                )
                # 세션 참가자로도 추가
                existing = await SessionParticipant.get_or_none(session=session, club_member=member)
                if not existing:
                    await SessionParticipant.create(
                        session=session,
                        club_member=member,
                        participant_category=ParticipantCategory.MEMBER
                    )
            elif guest:
                await MatchParticipant.create(
                    match=match,
                    guest=guest,
                    participant_category=ParticipantCategory.GUEST,
                    team=Team.B,
                    position=idx
                )
                # 세션 참가자로도 추가
                existing = await SessionParticipant.get_or_none(session=session, guest=guest)
                if not existing:
                    await SessionParticipant.create(
                        session=session,
                        guest=guest,
                        participant_category=ParticipantCategory.GUEST
                    )
            else:
                unmatched_players.append(player_name)

        # 경기 결과 저장
        winner = None
        if match_data.team_a.score > match_data.team_b.score:
            winner = Team.A
        elif match_data.team_b.score > match_data.team_a.score:
            winner = Team.B

        await MatchResult.create(
            match=match,
            team_a_score=match_data.team_a.score,
            team_b_score=match_data.team_b.score,
            winner_team=winner,
            recorded_by=membership.user
        )

        created_matches.append(match.id)

    response = {
        "message": f"{len(created_matches)}개의 경기가 저장되었습니다",
        "session_id": session.id,
        "match_ids": created_matches,
        "unmatched_players": list(set(unmatched_players)) if unmatched_players else None
    }

    if created_season_id:
        response["created_season_id"] = created_season_id

    return response
