"""
세션 관리 API

시간 처리:
- 클라이언트에서 date + start_time + end_time을 KST 기준으로 전송
- 서버에서 UTC datetime으로 변환하여 저장
- 응답 시 UTC → KST 변환하여 반환
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import date, time, datetime, timedelta
from pydantic import BaseModel as PydanticBase, Field
from app.models.club import Club
from app.models.event import Event, Session, SessionParticipant, SessionStatus, SessionType, EventType, ParticipantCategory, ParticipationType
from app.models.match import Match, MatchParticipant, MatchResult, MatchType, MatchStatus, Team, ParticipantCategory as MatchParticipantCategory
from app.models.member import ClubMember, MemberRole, MemberStatus
from app.models.guest import Guest
from app.models.user import User
from app.models.season import Season
from app.core.dependencies import (
    get_current_active_user,
    require_club_manager,
    get_club_or_404
)
from app.core.timezone import KST, to_utc, to_kst

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/clubs/{club_id}/sessions", tags=["세션 관리"])


class SessionCreate(PydanticBase):
    """
    세션 생성 요청

    시간 필드는 KST 기준으로 전송:
    - date: 세션 날짜 (예: 2026-01-31)
    - start_time: 시작 시간 (예: 09:00)
    - end_time: 종료 시간 (예: 12:00)
    """
    title: Optional[str] = Field(None, max_length=200)
    date: date
    start_time: time
    end_time: time
    location: Optional[str] = Field(None, max_length=200)
    num_courts: int = Field(..., ge=1, le=20)
    match_duration_minutes: int = Field(30, ge=10, le=120)
    break_duration_minutes: int = Field(5, ge=0, le=30)
    warmup_duration_minutes: int = Field(10, ge=0, le=60)
    session_type: str = Field("league", pattern="^(league|tournament)$")
    season_id: Optional[int] = None

    def to_utc_datetimes(self) -> tuple[datetime, datetime]:
        """date + time을 UTC datetime으로 변환"""
        # KST datetime 생성
        start_kst = datetime.combine(self.date, self.start_time, tzinfo=KST)
        end_kst = datetime.combine(self.date, self.end_time, tzinfo=KST)

        # 종료 시간이 시작 시간보다 이른 경우 (자정 넘김)
        if self.end_time <= self.start_time:
            end_kst = end_kst + timedelta(days=1)

        # UTC로 변환
        return to_utc(start_kst), to_utc(end_kst)


class MatchParticipantData(PydanticBase):
    """경기 참가자 데이터"""
    category: str  # member, guest, associate
    member_id: Optional[int] = None
    guest_id: Optional[int] = None
    user_id: Optional[int] = None


class MatchCreate(PydanticBase):
    court_number: int
    match_type: str
    team_a: List[MatchParticipantData] = []
    team_b: List[MatchParticipantData] = []
    # 하위 호환성을 위해 기존 필드 유지
    team_a_members: List[int] = []
    team_b_members: List[int] = []


class MatchUpdate(PydanticBase):
    team_a_score: Optional[int] = None
    team_b_score: Optional[int] = None


class ParticipantAdd(PydanticBase):
    """참가자 추가 요청"""
    category: str  # member, guest, associate
    member_id: Optional[int] = None  # category가 member일 때
    guest_id: Optional[int] = None   # category가 guest일 때
    user_id: Optional[int] = None    # category가 associate일 때
    participation_type: Optional[str] = None  # mens_doubles, mixed_doubles, singles


async def get_session_or_404(session_id: int, club_id: int) -> Session:
    """세션 조회 또는 404"""
    session = await Session.get_or_none(id=session_id, is_deleted=False).prefetch_related("event", "season")
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="세션을 찾을 수 없습니다"
        )

    session_club_id = await get_session_club_id(session)
    if session_club_id != club_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="세션을 찾을 수 없습니다"
        )
    return session


async def get_session_club_id(session: Session) -> Optional[int]:
    """세션의 club_id를 반환 (event 또는 season 통해)"""
    if session.event:
        return session.event.club_id
    elif session.season:
        return session.season.club_id
    return None


def format_participant_data(p, include_team: bool = False) -> dict:
    """참가자 정보 포맷팅 공통 함수"""
    data = {
        "id": p.id,
        "category": p.participant_category.value,
    }

    # 이름/성별 정보 추가 (SessionParticipant의 경우)
    if hasattr(p, 'get_participant_name'):
        data["name"] = p.get_participant_name()
        data["gender"] = p.get_participant_gender()

    # 팀 정보 추가 (MatchParticipant의 경우)
    if include_team and hasattr(p, 'team'):
        data["team"] = p.team.value

    # 연결된 엔티티 정보
    if p.club_member:
        data["member_id"] = p.club_member_id
        if p.club_member.user:
            data["user_id"] = p.club_member.user_id
            if include_team:
                data["member"] = {
                    "id": p.club_member.id,
                    "user": {
                        "name": p.club_member.user.name,
                        "gender": p.club_member.user.gender,
                    }
                }
    elif p.guest:
        data["guest_id"] = p.guest_id
        if include_team:
            data["guest"] = {"id": p.guest.id, "name": p.guest.name, "gender": getattr(p.guest, 'gender', None)}
    elif p.user:
        data["user_id"] = p.user_id
        if include_team:
            data["user"] = {"id": p.user.id, "name": p.user.name, "gender": getattr(p.user, 'gender', None)}

    return data


@router.get("")
async def list_sessions(
    club_id: int,
    season_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user)
):
    """세션 목록 조회"""
    club = await get_club_or_404(club_id)

    # 시즌 필터링 또는 이벤트 기반 조회
    if season_id:
        sessions = await Session.filter(
            season_id=season_id, is_deleted=False
        ).prefetch_related("season", "participants__club_member__user").order_by("-start_datetime")
    else:
        # 기존 이벤트 기반 조회 (하위 호환성)
        sessions = await Session.filter(
            event__club=club, is_deleted=False
        ).prefetch_related("event", "season", "participants__club_member__user").order_by("-start_datetime")

    return [{
        "id": s.id,
        "title": s.title,
        # 하위 호환: date, start_time, end_time (KST 기준, 프로퍼티에서 변환)
        "date": s.date.isoformat(),
        "start_time": s.start_time.isoformat(),
        "end_time": s.end_time.isoformat(),
        # 정확한 datetime (KST 변환)
        "start_datetime": to_kst(s.start_datetime).isoformat(),
        "end_datetime": to_kst(s.end_datetime).isoformat(),
        "location": s.location,
        "num_courts": s.num_courts,
        "match_duration_minutes": s.match_duration_minutes,
        "break_duration_minutes": s.break_duration_minutes,
        "warmup_duration_minutes": s.warmup_duration_minutes,
        "session_type": s.session_type.value if s.session_type else "league",
        "status": s.status.value,
        "season_id": s.season_id,
        "season_name": s.season.name if s.season else None,
        "participant_count": len(s.participants),
    } for s in sessions]


@router.post("")
async def create_session(
    club_id: int,
    session_data: SessionCreate,
    membership: ClubMember = Depends(require_club_manager)
):
    """세션 생성"""

    # 시즌 확인 (선택사항)
    season = None
    if session_data.season_id:
        season = await Season.get_or_none(id=session_data.season_id, club_id=club_id, is_deleted=False)
        if not season:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="시즌을 찾을 수 없습니다"
            )

    # 기본 이벤트 찾기 또는 생성 (시즌이 없는 경우)
    event = None
    if not season:
        event = await Event.get_or_none(club_id=club_id, event_type=EventType.REGULAR)
        if not event:
            event = await Event.create(
                club_id=club_id,
                title="정기 모임",
                event_type=EventType.REGULAR
            )

    # KST date+time → UTC datetime 변환
    start_datetime_utc, end_datetime_utc = session_data.to_utc_datetimes()

    session = await Session.create(
        event=event,
        season=season,
        title=session_data.title,
        start_datetime=start_datetime_utc,
        end_datetime=end_datetime_utc,
        location=session_data.location,
        num_courts=session_data.num_courts,
        match_duration_minutes=session_data.match_duration_minutes,
        break_duration_minutes=session_data.break_duration_minutes,
        warmup_duration_minutes=session_data.warmup_duration_minutes,
        session_type=SessionType(session_data.session_type),
        status=SessionStatus.CONFIRMED
    )

    return {
        "id": session.id,
        "title": session.title,
        # 하위 호환: date, start_time, end_time (KST 기준)
        "date": session.date.isoformat(),
        "start_time": session.start_time.isoformat(),
        "end_time": session.end_time.isoformat(),
        # 정확한 datetime (KST 변환)
        "start_datetime": to_kst(session.start_datetime).isoformat(),
        "end_datetime": to_kst(session.end_datetime).isoformat(),
        "location": session.location,
        "num_courts": session.num_courts,
        "match_duration_minutes": session.match_duration_minutes,
        "break_duration_minutes": session.break_duration_minutes,
        "warmup_duration_minutes": session.warmup_duration_minutes,
        "session_type": session.session_type.value,
        "status": session.status.value,
        "season_id": session.season_id,
    }


@router.get("/{session_id}")
async def get_session(
    club_id: int,
    session_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """세션 상세 조회 (참가자 포함)"""
    # 기본 세션 검증
    await get_session_or_404(session_id, club_id)

    # 전체 데이터 prefetch
    session = await Session.get(id=session_id).prefetch_related(
        "event",
        "season",
        "participants__club_member__user",
        "participants__guest",
        "participants__user",
        "matches__participants__club_member__user",
        "matches__participants__guest",
        "matches__participants__user",
        "matches__result"
    )

    # 공통 함수 사용하여 참가자 포맷팅
    participants = [format_participant_data(p) for p in session.participants]

    # 배치 쿼리로 모든 경기 결과 조회 (N+1 방지)
    match_ids = [m.id for m in session.matches]
    results_map = {}
    if match_ids:
        results = await MatchResult.filter(match_id__in=match_ids)
        results_map = {r.match_id: r for r in results}

    matches = []
    for m in session.matches:
        team_a = [p for p in m.participants if p.team == Team.A]
        team_b = [p for p in m.participants if p.team == Team.B]

        # prefetch된 결과 사용 (N+1 쿼리 제거)
        result = results_map.get(m.id)

        matches.append({
            "id": m.id,
            "court_number": m.court_number,
            "match_type": m.match_type.value,
            "status": m.status.value,
            "team_a": [format_participant_data(p) for p in team_a],
            "team_b": [format_participant_data(p) for p in team_b],
            "score": {
                "team_a": result.team_a_score if result else None,
                "team_b": result.team_b_score if result else None,
            } if result else None
        })

    return {
        "id": session.id,
        "title": session.title,
        # 하위 호환: date, start_time, end_time (KST 기준)
        "date": session.date.isoformat(),
        "start_time": session.start_time.isoformat(),
        "end_time": session.end_time.isoformat(),
        # 정확한 datetime (KST 변환)
        "start_datetime": to_kst(session.start_datetime).isoformat(),
        "end_datetime": to_kst(session.end_datetime).isoformat(),
        "location": session.location,
        "num_courts": session.num_courts,
        "match_duration_minutes": session.match_duration_minutes,
        "break_duration_minutes": session.break_duration_minutes,
        "warmup_duration_minutes": session.warmup_duration_minutes,
        "session_type": session.session_type.value if session.session_type else "league",
        "status": session.status.value,
        "season_id": session.season_id,
        "season_name": session.season.name if session.season else None,
        "participants": participants,
        "matches": matches,
    }


@router.post("/{session_id}/participants")
async def add_participant(
    club_id: int,
    session_id: int,
    participant_data: ParticipantAdd,
    membership: ClubMember = Depends(require_club_manager)
):
    """참가자 추가 (회원/게스트/준회원)"""
    session = await get_session_or_404(session_id, club_id)

    category = ParticipantCategory(participant_data.category)
    participation_type = ParticipationType(participant_data.participation_type) if participant_data.participation_type else None

    if category == ParticipantCategory.MEMBER:
        # 정회원 추가
        if not participant_data.member_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="회원 ID가 필요합니다"
            )
        member = await ClubMember.get_or_none(id=participant_data.member_id, club_id=club_id, is_deleted=False)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="회원을 찾을 수 없습니다"
            )

        # 중복 체크
        existing = await SessionParticipant.get_or_none(session=session, club_member=member)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 참가 중인 회원입니다"
            )

        await SessionParticipant.create(
            session=session,
            club_member=member,
            participant_category=ParticipantCategory.MEMBER,
            participation_type=participation_type
        )

    elif category == ParticipantCategory.GUEST:
        # 게스트 추가
        if not participant_data.guest_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="게스트 ID가 필요합니다"
            )
        guest = await Guest.get_or_none(id=participant_data.guest_id, club_id=club_id, is_deleted=False)
        if not guest:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="게스트를 찾을 수 없습니다"
            )

        # 중복 체크
        existing = await SessionParticipant.get_or_none(session=session, guest=guest)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 참가 중인 게스트입니다"
            )

        await SessionParticipant.create(
            session=session,
            guest=guest,
            participant_category=ParticipantCategory.GUEST,
            participation_type=participation_type
        )

    elif category == ParticipantCategory.ASSOCIATE:
        # 준회원 추가 (시스템 가입 유저, 동호회 미가입)
        if not participant_data.user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="사용자 ID가 필요합니다"
            )
        user = await User.get_or_none(id=participant_data.user_id, is_deleted=False)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다"
            )

        # 동호회 회원인지 확인 (회원이면 준회원으로 추가 불가)
        is_member = await ClubMember.exists(club_id=club_id, user=user, is_deleted=False)
        if is_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 동호회 회원입니다. 회원으로 추가해주세요."
            )

        # 중복 체크
        existing = await SessionParticipant.get_or_none(session=session, user=user)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 참가 중인 준회원입니다"
            )

        await SessionParticipant.create(
            session=session,
            user=user,
            participant_category=ParticipantCategory.ASSOCIATE,
            participation_type=participation_type
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="잘못된 참가자 유형입니다"
        )

    return {"message": "참가자가 추가되었습니다"}


@router.delete("/{session_id}/participants/{participant_id}")
async def remove_participant(
    club_id: int,
    session_id: int,
    participant_id: int,
    membership: ClubMember = Depends(require_club_manager)
):
    """참가자 제거 (participant_id 또는 member_id로)"""

    # participant_id로 먼저 시도
    participant = await SessionParticipant.get_or_none(id=participant_id, session_id=session_id)

    # 없으면 member_id로 시도
    if not participant:
        participant = await SessionParticipant.get_or_none(
            session_id=session_id,
            club_member_id=participant_id
        )

    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="참가자를 찾을 수 없습니다"
        )

    await participant.delete()
    return {"message": "참가자가 제거되었습니다"}


@router.post("/{session_id}/join")
async def join_session(
    club_id: int,
    session_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """현재 사용자가 세션에 참가 (회원 자신이 참가 신청)"""
    session = await get_session_or_404(session_id, club_id)

    # 현재 사용자의 클럽 멤버십 확인
    member = await ClubMember.get_or_none(
        club_id=club_id,
        user=current_user,
        is_deleted=False,
        status=MemberStatus.ACTIVE
    )

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 동호회의 활성 회원만 참가할 수 있습니다"
        )

    # 이미 참가 중인지 확인
    existing = await SessionParticipant.get_or_none(session=session, club_member=member)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 참가 중입니다"
        )

    await SessionParticipant.create(
        session=session,
        club_member=member,
        participant_category=ParticipantCategory.MEMBER
    )

    return {"message": "세션에 참가했습니다", "is_participating": True}


@router.delete("/{session_id}/join")
async def leave_session(
    club_id: int,
    session_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """현재 사용자가 세션에서 불참 (회원 자신이 참가 취소)"""
    session = await get_session_or_404(session_id, club_id)

    # 현재 사용자의 클럽 멤버십 확인
    member = await ClubMember.get_or_none(
        club_id=club_id,
        user=current_user,
        is_deleted=False
    )

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 동호회의 회원이 아닙니다"
        )

    # 참가 중인지 확인
    participant = await SessionParticipant.get_or_none(session=session, club_member=member)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="참가 중이 아닙니다"
        )

    await participant.delete()
    return {"message": "참가를 취소했습니다", "is_participating": False}


@router.get("/{session_id}/my-participation")
async def get_my_participation(
    club_id: int,
    session_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """현재 사용자의 세션 참가 여부 확인"""
    session = await get_session_or_404(session_id, club_id)

    # 현재 사용자의 클럽 멤버십 확인
    member = await ClubMember.get_or_none(
        club_id=club_id,
        user=current_user,
        is_deleted=False
    )

    if not member:
        return {"is_participating": False, "is_member": False}

    # 참가 중인지 확인
    participant = await SessionParticipant.get_or_none(session=session, club_member=member)

    return {
        "is_participating": participant is not None,
        "is_member": True,
        "member_id": member.id,
        "participant_id": participant.id if participant else None
    }


@router.post("/{session_id}/participants/{member_id}")
async def add_member_participant(
    club_id: int,
    session_id: int,
    member_id: int,
    membership: ClubMember = Depends(require_club_manager)
):
    """멤버 참가자 간편 추가 (member_id 직접 사용)"""
    session = await get_session_or_404(session_id, club_id)

    member = await ClubMember.get_or_none(id=member_id, club_id=club_id, is_deleted=False)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="회원을 찾을 수 없습니다"
        )

    # 중복 체크
    existing = await SessionParticipant.get_or_none(session=session, club_member=member)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 참가 중인 회원입니다"
        )

    await SessionParticipant.create(
        session=session,
        club_member=member,
        participant_category=ParticipantCategory.MEMBER
    )

    return {"message": "참가자가 추가되었습니다"}


@router.post("/{session_id}/matches")
async def create_match(
    club_id: int,
    session_id: int,
    match_data: MatchCreate,
    membership: ClubMember = Depends(require_club_manager)
):
    """경기 생성"""
    session = await get_session_or_404(session_id, club_id)

    # 경기 번호 자동 생성
    match_count = await Match.filter(session=session).count()

    match = await Match.create(
        session=session,
        match_number=match_count + 1,
        court_number=match_data.court_number,
        scheduled_datetime=session.start_datetime,  # UTC datetime
        match_type=match_data.match_type,
        status=MatchStatus.SCHEDULED
    )

    async def add_match_participant(participant_data: MatchParticipantData, team: Team, position: int):
        """경기 참가자 추가 헬퍼 함수"""
        category = MatchParticipantCategory(participant_data.category)

        if category == MatchParticipantCategory.MEMBER:
            # 테넌트 격리: club_id 필터 추가
            member = await ClubMember.get_or_none(
                id=participant_data.member_id,
                club_id=club_id,
                is_deleted=False
            )
            if member:
                await MatchParticipant.create(
                    match=match,
                    club_member=member,
                    participant_category=MatchParticipantCategory.MEMBER,
                    team=team,
                    position=position
                )
        elif category == MatchParticipantCategory.GUEST:
            # 테넌트 격리: club_id 필터 추가
            guest = await Guest.get_or_none(
                id=participant_data.guest_id,
                club_id=club_id,
                is_deleted=False
            )
            if guest:
                await MatchParticipant.create(
                    match=match,
                    guest=guest,
                    participant_category=MatchParticipantCategory.GUEST,
                    team=team,
                    position=position
                )
        elif category == MatchParticipantCategory.ASSOCIATE:
            user = await User.get_or_none(id=participant_data.user_id, is_deleted=False)
            if user:
                await MatchParticipant.create(
                    match=match,
                    user=user,
                    participant_category=MatchParticipantCategory.ASSOCIATE,
                    team=team,
                    position=position
                )

    # 새 형식 (team_a, team_b) 사용
    if match_data.team_a:
        for idx, participant in enumerate(match_data.team_a, 1):
            await add_match_participant(participant, Team.A, idx)
    # 하위 호환성: 기존 형식 (team_a_members) 사용
    elif match_data.team_a_members:
        for idx, member_id in enumerate(match_data.team_a_members, 1):
            # 테넌트 격리: club_id 필터 추가
            member = await ClubMember.get_or_none(id=member_id, club_id=club_id, is_deleted=False)
            if member:
                await MatchParticipant.create(
                    match=match,
                    club_member=member,
                    participant_category=MatchParticipantCategory.MEMBER,
                    team=Team.A,
                    position=idx
                )

    # 새 형식 (team_a, team_b) 사용
    if match_data.team_b:
        for idx, participant in enumerate(match_data.team_b, 1):
            await add_match_participant(participant, Team.B, idx)
    # 하위 호환성: 기존 형식 (team_b_members) 사용
    elif match_data.team_b_members:
        for idx, member_id in enumerate(match_data.team_b_members, 1):
            # 테넌트 격리: club_id 필터 추가
            member = await ClubMember.get_or_none(id=member_id, club_id=club_id, is_deleted=False)
            if member:
                await MatchParticipant.create(
                    match=match,
                    club_member=member,
                    participant_category=MatchParticipantCategory.MEMBER,
                    team=Team.B,
                    position=idx
                )

    return {"id": match.id, "message": "경기가 생성되었습니다"}


@router.put("/{session_id}/matches/{match_id}")
async def update_match(
    club_id: int,
    session_id: int,
    match_id: int,
    match_data: MatchUpdate,
    membership: ClubMember = Depends(require_club_manager)
):
    """경기 결과 업데이트 (자동 저장)"""
    await get_session_or_404(session_id, club_id)

    # 점수 검증
    if match_data.team_a_score is not None and match_data.team_a_score < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="점수는 0 이상이어야 합니다"
        )
    if match_data.team_b_score is not None and match_data.team_b_score < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="점수는 0 이상이어야 합니다"
        )

    match = await Match.get_or_none(id=match_id, session_id=session_id)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="경기를 찾을 수 없습니다"
        )

    # 결과 업데이트 또는 생성
    result = await MatchResult.get_or_none(match=match)

    if result:
        if match_data.team_a_score is not None:
            result.team_a_score = match_data.team_a_score
        if match_data.team_b_score is not None:
            result.team_b_score = match_data.team_b_score

        # 승자 결정
        if result.team_a_score > result.team_b_score:
            result.winner_team = Team.A
        elif result.team_b_score > result.team_a_score:
            result.winner_team = Team.B

        await result.save()
    else:
        if match_data.team_a_score is not None and match_data.team_b_score is not None:
            winner = None
            if match_data.team_a_score > match_data.team_b_score:
                winner = Team.A
            elif match_data.team_b_score > match_data.team_a_score:
                winner = Team.B

            # 현재 사용자 조회
            user = await membership.user
            result = await MatchResult.create(
                match=match,
                team_a_score=match_data.team_a_score,
                team_b_score=match_data.team_b_score,
                sets_detail={},
                winner_team=winner,
                recorded_by=user
            )

    match.status = MatchStatus.COMPLETED
    await match.save()

    return {"message": "경기 결과가 저장되었습니다"}


@router.get("/{session_id}/matches")
async def list_matches(
    club_id: int,
    session_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """세션의 경기 목록 조회"""
    session = await get_session_or_404(session_id, club_id)

    matches = await Match.filter(session=session).prefetch_related(
        "participants__club_member__user",
        "participants__guest",
        "participants__user"
    ).order_by("match_number")

    # 배치 쿼리로 모든 경기 결과 조회 (N+1 방지)
    match_ids = [m.id for m in matches]
    results_map = {}
    if match_ids:
        results = await MatchResult.filter(match_id__in=match_ids)
        results_map = {r.match_id: r for r in results}

    result = []
    for m in matches:
        # prefetch된 결과 사용
        match_result = results_map.get(m.id)

        result.append({
            "id": m.id,
            "match_number": m.match_number,
            "court_number": m.court_number,
            "match_type": m.match_type.value,
            "status": m.status.value,
            "participants": [format_participant_data(p, include_team=True) for p in m.participants],
            "score_a": match_result.team_a_score if match_result else None,
            "score_b": match_result.team_b_score if match_result else None,
        })

    return result


@router.get("/{session_id}/participants")
async def list_participants(
    club_id: int,
    session_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """세션의 참가자 목록 조회"""
    session = await get_session_or_404(session_id, club_id)

    participants = await SessionParticipant.filter(session=session).prefetch_related(
        "club_member__user",
        "guest",
        "user"
    )

    # 공통 함수 사용하여 참가자 포맷팅
    return [format_participant_data(p, include_team=True) for p in participants]


@router.delete("/{session_id}")
async def delete_session(
    club_id: int,
    session_id: int,
    membership: ClubMember = Depends(require_club_manager)
):
    """세션 삭제"""
    session = await get_session_or_404(session_id, club_id)
    session.is_deleted = True
    await session.save()
    return {"message": "세션이 삭제되었습니다"}


@router.put("/{session_id}")
async def update_session(
    club_id: int,
    session_id: int,
    session_data: SessionCreate,
    membership: ClubMember = Depends(require_club_manager)
):
    """세션 수정"""
    session = await get_session_or_404(session_id, club_id)

    if session_data.title is not None:
        session.title = session_data.title
    if session_data.location is not None:
        session.location = session_data.location
    if session_data.session_type is not None:
        session.session_type = SessionType(session_data.session_type)

    # 날짜/시간이 변경된 경우 UTC datetime으로 변환
    if session_data.date is not None or session_data.start_time is not None or session_data.end_time is not None:
        start_datetime_utc, end_datetime_utc = session_data.to_utc_datetimes()
        session.start_datetime = start_datetime_utc
        session.end_datetime = end_datetime_utc

    # 시즌 연결 변경
    if session_data.season_id is not None:
        # 시즌 검증
        season = await Season.get_or_none(id=session_data.season_id, club_id=club_id, is_deleted=False)
        if not season:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="시즌을 찾을 수 없습니다"
            )
        session.season = season
    # season_id가 명시적으로 전달되지 않았으면 기존 값 유지 (None이 아닌 경우에만 처리)

    await session.save()

    return {
        "id": session.id,
        "title": session.title,
        "date": session.date.isoformat(),
        "start_time": session.start_time.isoformat(),
        "end_time": session.end_time.isoformat(),
        "start_datetime": to_kst(session.start_datetime).isoformat(),
        "end_datetime": to_kst(session.end_datetime).isoformat(),
        "location": session.location,
        "session_type": session.session_type.value if session.session_type else "league",
    }


@router.post("/{session_id}/matches/generate")
async def generate_matches(
    club_id: int,
    session_id: int,
    membership: ClubMember = Depends(require_club_manager)
):
    """경기 자동 생성"""
    # 기본 세션 검증
    await get_session_or_404(session_id, club_id)

    # 참가자 데이터 포함하여 다시 조회
    session = await Session.get(id=session_id).prefetch_related(
        "event", "season", "participants__club_member__user",
        "participants__guest", "participants__user"
    )

    if len(session.participants) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="최소 2명의 참가자가 필요합니다"
        )

    # 기존 경기 삭제
    await Match.filter(session=session).delete()

    # 참가자 분류
    males = []
    females = []
    for p in session.participants:
        gender = None
        if p.club_member and p.club_member.user:
            gender = p.club_member.user.gender
        elif p.guest:
            gender = p.guest.gender
        elif p.user:
            gender = p.user.gender

        if gender == "male":
            males.append(p)
        elif gender == "female":
            females.append(p)

    import random
    random.shuffle(males)
    random.shuffle(females)

    matches_created = []
    match_number = 0

    # 혼합 복식 생성 (남녀 짝)
    while len(males) >= 2 and len(females) >= 2:
        match_number += 1
        match = await Match.create(
            session=session,
            match_number=match_number,
            court_number=(match_number - 1) % session.num_courts + 1,
            scheduled_datetime=session.start_datetime,
            match_type=MatchType.MIXED_DOUBLES,
            status=MatchStatus.SCHEDULED
        )

        # 팀 A: 남1 + 여1
        m1, m2 = males.pop(0), males.pop(0)
        f1, f2 = females.pop(0), females.pop(0)

        for p, team in [(m1, Team.A), (f1, Team.A), (m2, Team.B), (f2, Team.B)]:
            await MatchParticipant.create(
                match=match,
                club_member=p.club_member,
                guest=p.guest,
                user=p.user,
                participant_category=p.participant_category,
                team=team,
                position=1
            )

        matches_created.append(match.id)

    # 남자 복식 생성
    while len(males) >= 4:
        match_number += 1
        match = await Match.create(
            session=session,
            match_number=match_number,
            court_number=(match_number - 1) % session.num_courts + 1,
            scheduled_datetime=session.start_datetime,
            match_type=MatchType.MENS_DOUBLES,
            status=MatchStatus.SCHEDULED
        )

        for i, team in enumerate([Team.A, Team.A, Team.B, Team.B]):
            p = males.pop(0)
            await MatchParticipant.create(
                match=match,
                club_member=p.club_member,
                guest=p.guest,
                user=p.user,
                participant_category=p.participant_category,
                team=team,
                position=1
            )

        matches_created.append(match.id)

    # 여자 복식 생성
    while len(females) >= 4:
        match_number += 1
        match = await Match.create(
            session=session,
            match_number=match_number,
            court_number=(match_number - 1) % session.num_courts + 1,
            scheduled_datetime=session.start_datetime,
            match_type=MatchType.WOMENS_DOUBLES,
            status=MatchStatus.SCHEDULED
        )

        for i, team in enumerate([Team.A, Team.A, Team.B, Team.B]):
            p = females.pop(0)
            await MatchParticipant.create(
                match=match,
                club_member=p.club_member,
                guest=p.guest,
                user=p.user,
                participant_category=p.participant_category,
                team=team,
                position=1
            )

        matches_created.append(match.id)

    return {"message": f"{len(matches_created)}개의 경기가 생성되었습니다", "match_ids": matches_created}


class AIMatchGenerateRequest(PydanticBase):
    """AI 경기 생성 요청"""
    mode: str = Field("balanced", pattern="^(balanced|random)$")  # balanced: 실력 균형, random: 완전 랜덤
    match_duration_minutes: Optional[int] = Field(None, ge=10, le=120)
    break_duration_minutes: Optional[int] = Field(None, ge=0, le=30)


class AIMatchConfirmRequest(PydanticBase):
    """AI 생성 경기 확정 요청"""
    matches: List[dict]


@router.post("/{session_id}/matches/generate-ai")
async def generate_ai_matches(
    club_id: int,
    session_id: int,
    request: AIMatchGenerateRequest,
    membership: ClubMember = Depends(require_club_manager)
):
    """
    AI 기반 경기 자동 생성 (미리보기)

    - mode: "balanced" (실력 균형) 또는 "random" (완전 랜덤)
    - 생성된 매치를 미리보기로 반환하며, 확정하려면 confirm-ai 엔드포인트를 호출해야 합니다
    """
    from app.services.ai_matching_service import ai_matching_service
    from app.models.ranking import Ranking

    # 세션 검증 및 데이터 로드
    await get_session_or_404(session_id, club_id)
    session = await Session.get(id=session_id).prefetch_related(
        "event", "season", "participants__club_member__user",
        "participants__guest", "participants__user"
    )

    if len(session.participants) < 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="최소 4명의 참가자가 필요합니다 (복식 경기 1개)"
        )

    # 참가자 정보 수집 (랭킹 포함)
    participants_data = []
    for p in session.participants:
        participant_info = {
            "id": p.id,
            "name": p.get_participant_name(),
            "gender": p.get_participant_gender(),
            "match_type": p.participation_type.value if p.participation_type else None,
            "ranking": {"points": 0, "wins": 0, "losses": 0, "win_rate": 0}
        }

        # 회원인 경우 랭킹 정보 조회
        if p.club_member:
            ranking = await Ranking.get_or_none(club_id=club_id, club_member_id=p.club_member_id)
            if ranking:
                participant_info["ranking"] = {
                    "points": ranking.points,
                    "wins": ranking.wins,
                    "losses": ranking.losses,
                    "win_rate": ranking.win_rate
                }

        # match_type이 없으면 성별에 따라 기본값 설정
        if not participant_info["match_type"]:
            gender = participant_info["gender"]
            if gender == "male":
                participant_info["match_type"] = "mens_doubles"
            elif gender == "female":
                participant_info["match_type"] = "womens_doubles"
            else:
                participant_info["match_type"] = "mixed_doubles"

        participants_data.append(participant_info)

    # 세션 설정 (KST 기준 시간으로 AI에 전달)
    session_config = {
        "start_time": session.start_time.strftime("%H:%M"),  # KST 기준 (프로퍼티)
        "end_time": session.end_time.strftime("%H:%M"),      # KST 기준 (프로퍼티)
        "match_duration": request.match_duration_minutes or session.match_duration_minutes or 30,
        "break_duration": request.break_duration_minutes if request.break_duration_minutes is not None else (session.break_duration_minutes or 5),
        "num_courts": session.num_courts
    }

    try:
        result = await ai_matching_service.generate_matches(
            participants=participants_data,
            session_config=session_config,
            mode=request.mode
        )

        return {
            "preview": True,
            "mode": request.mode,
            "session_config": session_config,
            "matches": result["matches"],
            "summary": result["summary"]
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"AI 매칭 생성 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="경기 생성 중 오류가 발생했습니다"
        )


@router.post("/{session_id}/matches/confirm-ai")
async def confirm_ai_matches(
    club_id: int,
    session_id: int,
    request: AIMatchConfirmRequest,
    membership: ClubMember = Depends(require_club_manager)
):
    """
    AI 생성 경기 확정

    - generate-ai에서 받은 matches를 확정하여 실제 경기로 생성합니다
    - 기존 경기는 모두 삭제됩니다
    """
    session = await get_session_or_404(session_id, club_id)

    # 기존 경기 삭제
    await Match.filter(session_id=session_id).delete()

    # 참가자 매핑 (ID -> 실제 참가자)
    participants = await SessionParticipant.filter(session_id=session_id).prefetch_related(
        "club_member", "guest", "user"
    )
    participant_map = {p.id: p for p in participants}

    matches_created = []
    for match_data in request.matches:
        # 매치 타입 변환
        match_type_map = {
            "mens_doubles": MatchType.MENS_DOUBLES,
            "womens_doubles": MatchType.WOMENS_DOUBLES,
            "mixed_doubles": MatchType.MIXED_DOUBLES
        }
        match_type = match_type_map.get(match_data.get("match_type"), MatchType.MENS_DOUBLES)

        # 예약 시간 파싱 (KST 시간 문자열 → UTC datetime)
        scheduled_time_str = match_data.get("scheduled_time", session.start_time.strftime("%H:%M"))
        try:
            hour, minute = map(int, scheduled_time_str.split(":"))
            # 세션 날짜 + 예약 시간 → KST datetime → UTC datetime
            scheduled_kst = datetime.combine(session.date, time(hour, minute), tzinfo=KST)
            scheduled_datetime_utc = to_utc(scheduled_kst)
        except:
            scheduled_datetime_utc = session.start_datetime

        # 경기 생성
        match = await Match.create(
            session_id=session_id,
            match_number=match_data.get("match_number", len(matches_created) + 1),
            court_number=match_data.get("court_number", 1),
            scheduled_datetime=scheduled_datetime_utc,  # UTC datetime
            match_type=match_type,
            status=MatchStatus.SCHEDULED
        )

        # 팀 A 참가자 추가
        team_a_ids = match_data.get("team_a", {}).get("player_ids", [])
        for idx, player_id in enumerate(team_a_ids, 1):
            participant = participant_map.get(player_id)
            if participant:
                await MatchParticipant.create(
                    match=match,
                    club_member=participant.club_member,
                    guest=participant.guest,
                    user=participant.user,
                    participant_category=participant.participant_category,
                    team=Team.A,
                    position=idx
                )

        # 팀 B 참가자 추가
        team_b_ids = match_data.get("team_b", {}).get("player_ids", [])
        for idx, player_id in enumerate(team_b_ids, 1):
            participant = participant_map.get(player_id)
            if participant:
                await MatchParticipant.create(
                    match=match,
                    club_member=participant.club_member,
                    guest=participant.guest,
                    user=participant.user,
                    participant_category=participant.participant_category,
                    team=Team.B,
                    position=idx
                )

        matches_created.append(match.id)

    return {
        "message": f"{len(matches_created)}개의 경기가 생성되었습니다",
        "match_ids": matches_created
    }


class ScheduleCalculateRequest(PydanticBase):
    """스케줄 계산 요청"""
    start_time: time  # 시작 시간 (KST)
    end_time: time    # 종료 시간 (KST)
    num_courts: int = Field(..., ge=1, le=20)
    match_duration_minutes: int = Field(30, ge=10, le=120)
    break_duration_minutes: int = Field(5, ge=0, le=30)
    warmup_duration_minutes: int = Field(10, ge=0, le=60)


@router.post("/calculate-schedule")
async def calculate_session_schedule(
    club_id: int,
    request: ScheduleCalculateRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    세션 스케줄 계산 (미리보기용)

    워밍업 → 경기1 → 휴식 → 경기2 → 휴식 → ... → 종료시간 내 최대 경기 수 계산
    """
    await get_club_or_404(club_id)

    # 시간 계산 (분 단위)
    start_minutes = request.start_time.hour * 60 + request.start_time.minute
    end_minutes = request.end_time.hour * 60 + request.end_time.minute

    # 종료 시간이 시작 시간보다 이른 경우 (자정 넘김)
    if end_minutes <= start_minutes:
        end_minutes += 24 * 60

    total_minutes = end_minutes - start_minutes
    warmup = request.warmup_duration_minutes
    match_duration = request.match_duration_minutes
    break_duration = request.break_duration_minutes
    num_courts = request.num_courts

    # 워밍업 후 실제 경기 가능 시간
    available_minutes = total_minutes - warmup

    if available_minutes <= 0:
        return {
            "total_duration_minutes": total_minutes,
            "warmup_duration_minutes": warmup,
            "available_minutes": 0,
            "max_rounds": 0,
            "matches_per_round": num_courts,
            "total_matches": 0,
            "schedule": [],
            "actual_end_time": request.start_time.isoformat(),
            "utilization_percent": 0,
        }

    # 각 라운드는 (경기 시간 + 휴식 시간), 마지막 라운드는 휴식 불필요
    # 라운드 수 계산: available = match * rounds + break * (rounds - 1)
    # available = match * rounds + break * rounds - break
    # available + break = rounds * (match + break)
    # rounds = (available + break) / (match + break)

    if match_duration + break_duration > 0:
        max_rounds = (available_minutes + break_duration) // (match_duration + break_duration)
    else:
        max_rounds = 0

    # 최소 1라운드는 가능해야 함
    if max_rounds < 1 and available_minutes >= match_duration:
        max_rounds = 1

    # 스케줄 생성
    schedule = []
    current_time = start_minutes + warmup  # 워밍업 후 시작

    for round_num in range(1, max_rounds + 1):
        round_start_hour = (current_time // 60) % 24
        round_start_min = current_time % 60
        round_start_str = f"{round_start_hour:02d}:{round_start_min:02d}"

        round_end = current_time + match_duration
        round_end_hour = (round_end // 60) % 24
        round_end_min = round_end % 60
        round_end_str = f"{round_end_hour:02d}:{round_end_min:02d}"

        schedule.append({
            "round": round_num,
            "start_time": round_start_str,
            "end_time": round_end_str,
            "matches_count": num_courts,  # 코트 수만큼 동시 경기
            "type": "match",
        })

        current_time += match_duration

        # 마지막 라운드가 아니면 휴식 추가
        if round_num < max_rounds and break_duration > 0:
            break_end = current_time + break_duration
            break_end_hour = (break_end // 60) % 24
            break_end_min = break_end % 60

            schedule.append({
                "round": round_num,
                "start_time": round_end_str,
                "end_time": f"{break_end_hour:02d}:{break_end_min:02d}",
                "type": "break",
            })
            current_time += break_duration

    # 실제 종료 시간
    actual_end_hour = (current_time // 60) % 24
    actual_end_min = current_time % 60
    actual_end_str = f"{actual_end_hour:02d}:{actual_end_min:02d}"

    # 사용률 계산
    used_minutes = current_time - start_minutes
    utilization = (used_minutes / total_minutes * 100) if total_minutes > 0 else 0

    return {
        "total_duration_minutes": total_minutes,
        "warmup_duration_minutes": warmup,
        "warmup_end_time": f"{((start_minutes + warmup) // 60) % 24:02d}:{(start_minutes + warmup) % 60:02d}",
        "available_minutes": available_minutes,
        "max_rounds": max_rounds,
        "matches_per_round": num_courts,
        "total_matches": max_rounds * num_courts,
        "schedule": schedule,
        "actual_end_time": actual_end_str,
        "utilization_percent": round(utilization, 1),
    }
