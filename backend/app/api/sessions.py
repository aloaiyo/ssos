"""
세션 관리 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import date, time
from pydantic import BaseModel as PydanticBase
from app.models.club import Club
from app.models.event import Event, Session, SessionParticipant, SessionStatus, EventType, ParticipantCategory, ParticipationType
from app.models.match import Match, MatchParticipant, MatchResult, MatchType, MatchStatus, Team, ParticipantCategory as MatchParticipantCategory
from app.models.member import ClubMember, MemberRole, MemberStatus
from app.models.guest import Guest
from app.models.user import User
from app.core.dependencies import get_current_active_user

router = APIRouter(prefix="/clubs/{club_id}/sessions", tags=["세션 관리"])


class SessionCreate(PydanticBase):
    date: date
    start_time: time
    end_time: time
    num_courts: int
    match_duration_minutes: int = 30


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
async def list_sessions(
    club_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """세션 목록 조회"""
    club = await Club.get_or_none(id=club_id)
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="동호회를 찾을 수 없습니다"
        )
        
    sessions = await Session.filter(event__club=club).prefetch_related("event", "participants__club_member__user")
    
    return [{
        "id": s.id,
        "date": s.date.isoformat(),
        "start_time": s.start_time.isoformat(),
        "end_time": s.end_time.isoformat(),
        "num_courts": s.num_courts,
        "status": s.status.value,
        "participant_count": len(s.participants),
    } for s in sessions]


@router.post("")
async def create_session(
    club_id: int,
    session_data: SessionCreate,
    current_user: User = Depends(get_current_active_user)
):
    """세션 생성"""
    club = await check_manager_permission(club_id, current_user)
    
    # 기본 이벤트 찾기 또는 생성
    event = await Event.get_or_none(club=club, event_type=EventType.REGULAR)
    if not event:
        event = await Event.create(
            club=club,
            title="정기 모임",
            event_type=EventType.REGULAR
        )
    
    session = await Session.create(
        event=event,
        date=session_data.date,
        start_time=session_data.start_time,
        end_time=session_data.end_time,
        num_courts=session_data.num_courts,
        match_duration_minutes=session_data.match_duration_minutes,
        status=SessionStatus.CONFIRMED
    )
    
    return {
        "id": session.id,
        "date": session.date.isoformat(),
        "start_time": session.start_time.isoformat(),
        "end_time": session.end_time.isoformat(),
        "num_courts": session.num_courts,
        "status": session.status.value,
    }


@router.get("/{session_id}")
async def get_session(
    club_id: int,
    session_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """세션 상세 조회 (참가자 포함)"""
    session = await Session.get_or_none(id=session_id).prefetch_related(
        "event",
        "participants__club_member__user",
        "participants__guest",
        "participants__user",
        "matches__participants__club_member__user",
        "matches__participants__guest",
        "matches__participants__user",
        "matches__result"
    )

    if not session or session.event.club_id != club_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="세션을 찾을 수 없습니다"
        )

    participants = []
    for p in session.participants:
        participant_data = {
            "id": p.id,
            "category": p.participant_category.value,
            "name": p.get_participant_name(),
            "gender": p.get_participant_gender(),
        }

        if p.participant_category == ParticipantCategory.MEMBER and p.club_member:
            participant_data["member_id"] = p.club_member_id
            participant_data["user_id"] = p.club_member.user_id
        elif p.participant_category == ParticipantCategory.GUEST and p.guest:
            participant_data["guest_id"] = p.guest_id
        elif p.participant_category == ParticipantCategory.ASSOCIATE and p.user:
            participant_data["user_id"] = p.user_id

        participants.append(participant_data)

    def format_participant(p):
        """경기 참가자 정보 포맷팅"""
        data = {
            "id": p.id,
            "category": p.participant_category.value,
            "name": p.get_participant_name(),
            "gender": p.get_participant_gender(),
        }
        if p.participant_category == ParticipantCategory.MEMBER and p.club_member:
            data["member_id"] = p.club_member_id
        elif p.participant_category == ParticipantCategory.GUEST and p.guest:
            data["guest_id"] = p.guest_id
        elif p.participant_category == ParticipantCategory.ASSOCIATE and p.user:
            data["user_id"] = p.user_id
        return data

    matches = []
    for m in session.matches:
        team_a = [p for p in m.participants if p.team == Team.A]
        team_b = [p for p in m.participants if p.team == Team.B]

        # result is a OneToOne relation, prefetched - access via await or get_or_none
        try:
            result = await MatchResult.get_or_none(match_id=m.id)
        except Exception:
            result = None

        matches.append({
            "id": m.id,
            "court_number": m.court_number,
            "match_type": m.match_type.value,
            "status": m.status.value,
            "team_a": [format_participant(p) for p in team_a],
            "team_b": [format_participant(p) for p in team_b],
            "score": {
                "team_a": result.team_a_score if result else None,
                "team_b": result.team_b_score if result else None,
            } if result else None
        })

    return {
        "id": session.id,
        "date": session.date.isoformat(),
        "start_time": session.start_time.isoformat(),
        "end_time": session.end_time.isoformat(),
        "num_courts": session.num_courts,
        "status": session.status.value,
        "participants": participants,
        "matches": matches,
    }


@router.post("/{session_id}/participants")
async def add_participant(
    club_id: int,
    session_id: int,
    participant_data: ParticipantAdd,
    current_user: User = Depends(get_current_active_user)
):
    """참가자 추가 (회원/게스트/준회원)"""
    await check_manager_permission(club_id, current_user)

    session = await Session.get_or_none(id=session_id).prefetch_related("event")
    if not session or session.event.club_id != club_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="세션을 찾을 수 없습니다"
        )

    category = ParticipantCategory(participant_data.category)
    participation_type = ParticipationType(participant_data.participation_type) if participant_data.participation_type else None

    if category == ParticipantCategory.MEMBER:
        # 정회원 추가
        if not participant_data.member_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="회원 ID가 필요합니다"
            )
        member = await ClubMember.get_or_none(id=participant_data.member_id, club_id=club_id)
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
        guest = await Guest.get_or_none(id=participant_data.guest_id, club_id=club_id)
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
        user = await User.get_or_none(id=participant_data.user_id)
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
    current_user: User = Depends(get_current_active_user)
):
    """참가자 제거"""
    await check_manager_permission(club_id, current_user)

    participant = await SessionParticipant.get_or_none(id=participant_id, session_id=session_id)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="참가자를 찾을 수 없습니다"
        )

    await participant.delete()
    return {"message": "참가자가 제거되었습니다"}


@router.post("/{session_id}/matches")
async def create_match(
    club_id: int,
    session_id: int,
    match_data: MatchCreate,
    current_user: User = Depends(get_current_active_user)
):
    """경기 생성"""
    await check_manager_permission(club_id, current_user)

    session = await Session.get_or_none(id=session_id).prefetch_related("event")
    if not session or session.event.club_id != club_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="세션을 찾을 수 없습니다"
        )

    # 경기 번호 자동 생성
    match_count = await Match.filter(session=session).count()

    match = await Match.create(
        session=session,
        match_number=match_count + 1,
        court_number=match_data.court_number,
        scheduled_time=session.start_time,
        match_type=match_data.match_type,
        status=MatchStatus.SCHEDULED
    )

    async def add_match_participant(participant_data: MatchParticipantData, team: Team, position: int):
        """경기 참가자 추가 헬퍼 함수"""
        category = MatchParticipantCategory(participant_data.category)

        if category == MatchParticipantCategory.MEMBER:
            member = await ClubMember.get_or_none(id=participant_data.member_id)
            if member:
                await MatchParticipant.create(
                    match=match,
                    club_member=member,
                    participant_category=MatchParticipantCategory.MEMBER,
                    team=team,
                    position=position
                )
        elif category == MatchParticipantCategory.GUEST:
            guest = await Guest.get_or_none(id=participant_data.guest_id)
            if guest:
                await MatchParticipant.create(
                    match=match,
                    guest=guest,
                    participant_category=MatchParticipantCategory.GUEST,
                    team=team,
                    position=position
                )
        elif category == MatchParticipantCategory.ASSOCIATE:
            user = await User.get_or_none(id=participant_data.user_id)
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
            member = await ClubMember.get_or_none(id=member_id)
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
            member = await ClubMember.get_or_none(id=member_id)
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
    current_user: User = Depends(get_current_active_user)
):
    """경기 결과 업데이트 (자동 저장)"""
    await check_manager_permission(club_id, current_user)
    
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
                
            result = await MatchResult.create(
                match=match,
                team_a_score=match_data.team_a_score,
                team_b_score=match_data.team_b_score,
                sets_detail={},
                winner_team=winner,
                recorded_by=current_user
            )
    
    match.status = MatchStatus.COMPLETED
    await match.save()
    
    return {"message": "경기 결과가 저장되었습니다"}
