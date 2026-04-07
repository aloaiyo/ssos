"""
매칭 알고리즘 서비스

시간 처리:
- 모든 시간은 UTC datetime으로 처리
- start_datetime: 세션 시작 시간 (UTC)
- 경기 시간은 start_datetime + (match_index * duration)으로 계산
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.models.event import SessionParticipant, ParticipantCategory
from app.models.match import Match, MatchParticipant, MatchType, Team
from app.models.member import Gender
import random


def _create_match_participant_kwargs(participant: SessionParticipant, team: Team, position: int) -> dict:
    """참가자 유형에 따라 MatchParticipant 생성 인자 결정"""
    kwargs = {
        "team": team,
        "position": position,
        "participant_category": participant.participant_category,
    }
    if participant.participant_category == ParticipantCategory.GUEST:
        kwargs["guest"] = participant.guest
    elif participant.participant_category == ParticipantCategory.ASSOCIATE:
        kwargs["user"] = participant.user
    else:
        kwargs["club_member"] = participant.club_member
    return kwargs


async def create_matches_for_session(
    session_id: int,
    participants: List[SessionParticipant],
    num_courts: int,
    match_duration_minutes: int,
    start_datetime: datetime  # UTC datetime
) -> List[Match]:
    """
    세션에 대한 매치 생성

    간단한 라운드 로빈 방식으로 매칭
    """
    matches = []
    match_number = 1

    # 참가자를 타입별로 분류
    mens_doubles_participants = [
        p for p in participants
        if p.participation_type.value == "mens_doubles"
    ]
    mixed_doubles_participants = [
        p for p in participants
        if p.participation_type.value == "mixed_doubles"
    ]
    singles_participants = [
        p for p in participants
        if p.participation_type.value == "singles"
    ]

    # 남자 복식 매칭
    if len(mens_doubles_participants) >= 4:
        mens_matches = await _create_doubles_matches(
            session_id=session_id,
            participants=mens_doubles_participants,
            match_type=MatchType.MENS_DOUBLES,
            num_courts=num_courts,
            match_duration_minutes=match_duration_minutes,
            start_datetime=start_datetime,
            match_number_start=match_number
        )
        matches.extend(mens_matches)
        match_number += len(mens_matches)

    # 혼합 복식 매칭
    if len(mixed_doubles_participants) >= 4:
        mixed_matches = await _create_mixed_doubles_matches(
            session_id=session_id,
            participants=mixed_doubles_participants,
            num_courts=num_courts,
            match_duration_minutes=match_duration_minutes,
            start_datetime=start_datetime,
            match_number_start=match_number
        )
        matches.extend(mixed_matches)
        match_number += len(mixed_matches)

    # 단식 매칭
    if len(singles_participants) >= 2:
        singles_matches = await _create_singles_matches(
            session_id=session_id,
            participants=singles_participants,
            num_courts=num_courts,
            match_duration_minutes=match_duration_minutes,
            start_datetime=start_datetime,
            match_number_start=match_number
        )
        matches.extend(singles_matches)

    return matches


async def _create_doubles_matches(
    session_id: int,
    participants: List[SessionParticipant],
    match_type: MatchType,
    num_courts: int,
    match_duration_minutes: int,
    start_datetime: datetime,  # UTC datetime
    match_number_start: int
) -> List[Match]:
    """복식 매치 생성"""
    matches = []
    random.shuffle(participants)

    court = 1
    match_number = match_number_start
    current_datetime = start_datetime
    time_slot = 0

    # 4명씩 묶어서 매치 생성
    for i in range(0, len(participants) - 3, 4):
        team_a = participants[i:i+2]
        team_b = participants[i+2:i+4]

        match = await Match.create(
            session_id=session_id,
            match_number=match_number,
            court_number=court,
            scheduled_datetime=current_datetime,  # UTC datetime
            match_type=match_type
        )

        # 팀 A 참가자 추가
        for idx, participant in enumerate(team_a, 1):
            kwargs = _create_match_participant_kwargs(participant, Team.A, idx)
            await MatchParticipant.create(match=match, **kwargs)

        # 팀 B 참가자 추가
        for idx, participant in enumerate(team_b, 1):
            kwargs = _create_match_participant_kwargs(participant, Team.B, idx)
            await MatchParticipant.create(match=match, **kwargs)

        matches.append(match)
        match_number += 1

        # 다음 코트로 이동
        court += 1
        if court > num_courts:
            court = 1
            # 다음 시간대로 이동
            time_slot += 1
            current_datetime = start_datetime + timedelta(minutes=match_duration_minutes * time_slot)

    return matches


async def _create_mixed_doubles_matches(
    session_id: int,
    participants: List[SessionParticipant],
    num_courts: int,
    match_duration_minutes: int,
    start_datetime: datetime,  # UTC datetime
    match_number_start: int
) -> List[Match]:
    """혼합 복식 매치 생성 (남녀 페어링 고려)"""
    # 성별로 분류
    male_participants = []
    female_participants = []

    for p in participants:
        member = await p.club_member.select_related('user')
        if member.gender.value == Gender.MALE.value:
            male_participants.append(p)
        else:
            female_participants.append(p)

    random.shuffle(male_participants)
    random.shuffle(female_participants)

    matches = []
    court = 1
    match_number = match_number_start
    current_datetime = start_datetime
    time_slot = 0

    # 남녀 2명씩 팀 구성
    min_pairs = min(len(male_participants), len(female_participants))
    for i in range(0, min_pairs - 1, 2):
        if i + 1 >= min_pairs:
            break

        match = await Match.create(
            session_id=session_id,
            match_number=match_number,
            court_number=court,
            scheduled_datetime=current_datetime,  # UTC datetime
            match_type=MatchType.MIXED_DOUBLES
        )

        # 팀 A: 남1 + 여1
        kwargs = _create_match_participant_kwargs(male_participants[i], Team.A, 1)
        await MatchParticipant.create(match=match, **kwargs)
        kwargs = _create_match_participant_kwargs(female_participants[i], Team.A, 2)
        await MatchParticipant.create(match=match, **kwargs)

        # 팀 B: 남2 + 여2
        kwargs = _create_match_participant_kwargs(male_participants[i+1], Team.B, 1)
        await MatchParticipant.create(match=match, **kwargs)
        kwargs = _create_match_participant_kwargs(female_participants[i+1], Team.B, 2)
        await MatchParticipant.create(match=match, **kwargs)

        matches.append(match)
        match_number += 1

        court += 1
        if court > num_courts:
            court = 1
            time_slot += 1
            current_datetime = start_datetime + timedelta(minutes=match_duration_minutes * time_slot)

    return matches


async def _create_singles_matches(
    session_id: int,
    participants: List[SessionParticipant],
    num_courts: int,
    match_duration_minutes: int,
    start_datetime: datetime,  # UTC datetime
    match_number_start: int
) -> List[Match]:
    """단식 매치 생성"""
    matches = []
    random.shuffle(participants)

    court = 1
    match_number = match_number_start
    current_datetime = start_datetime
    time_slot = 0

    # 2명씩 묶어서 매치 생성
    for i in range(0, len(participants) - 1, 2):
        match = await Match.create(
            session_id=session_id,
            match_number=match_number,
            court_number=court,
            scheduled_datetime=current_datetime,  # UTC datetime
            match_type=MatchType.SINGLES
        )

        # 참가자 A
        kwargs = _create_match_participant_kwargs(participants[i], Team.A, 1)
        await MatchParticipant.create(match=match, **kwargs)

        # 참가자 B
        kwargs = _create_match_participant_kwargs(participants[i+1], Team.B, 1)
        await MatchParticipant.create(match=match, **kwargs)

        matches.append(match)
        match_number += 1

        court += 1
        if court > num_courts:
            court = 1
            time_slot += 1
            current_datetime = start_datetime + timedelta(minutes=match_duration_minutes * time_slot)

    return matches


async def generate_matches_for_session_inline(
    session,
) -> list:
    """
    세션의 참가자를 성별로 분류하여 자동으로 경기를 생성

    sessions.py의 generate_matches 엔드포인트에서 호출.
    트랜잭션은 호출자가 관리한다.

    Args:
        session: prefetch_related("participants__club_member__user",
                 "participants__guest", "participants__user")가 완료된 Session 객체

    Returns:
        생성된 Match ID 목록
    """
    import random as _random

    # 기존 경기 삭제
    await Match.filter(session=session).delete()

    # 참가자를 성별로 분류
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

    _random.shuffle(males)
    _random.shuffle(females)

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
            status="scheduled"
        )

        m1, m2 = males.pop(0), males.pop(0)
        f1, f2 = females.pop(0), females.pop(0)

        team_positions = {Team.A: 0, Team.B: 0}
        for p, team in [(m1, Team.A), (f1, Team.A), (m2, Team.B), (f2, Team.B)]:
            team_positions[team] += 1
            pos = team_positions[team]
            await MatchParticipant.create(
                match=match,
                club_member=p.club_member,
                guest=p.guest,
                user=p.user,
                participant_category=p.participant_category,
                team=team,
                position=pos
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
            status="scheduled"
        )

        team_positions = {Team.A: 0, Team.B: 0}
        for i, team in enumerate([Team.A, Team.A, Team.B, Team.B]):
            p = males.pop(0)
            team_positions[team] += 1
            pos = team_positions[team]
            await MatchParticipant.create(
                match=match,
                club_member=p.club_member,
                guest=p.guest,
                user=p.user,
                participant_category=p.participant_category,
                team=team,
                position=pos
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
            status="scheduled"
        )

        team_positions = {Team.A: 0, Team.B: 0}
        for i, team in enumerate([Team.A, Team.A, Team.B, Team.B]):
            p = females.pop(0)
            team_positions[team] += 1
            pos = team_positions[team]
            await MatchParticipant.create(
                match=match,
                club_member=p.club_member,
                guest=p.guest,
                user=p.user,
                participant_category=p.participant_category,
                team=team,
                position=pos
            )

        matches_created.append(match.id)

    return matches_created
