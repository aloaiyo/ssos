"""
매칭 알고리즘 서비스

시간 처리:
- 모든 시간은 UTC datetime으로 처리
- start_datetime: 세션 시작 시간 (UTC)
- 경기 시간은 start_datetime + (match_index * duration)으로 계산
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.models.event import SessionParticipant
from app.models.match import Match, MatchParticipant, MatchType, Team
from app.models.member import Gender
import random


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
            await MatchParticipant.create(
                match=match,
                club_member=participant.club_member,
                team=Team.A,
                position=idx
            )

        # 팀 B 참가자 추가
        for idx, participant in enumerate(team_b, 1):
            await MatchParticipant.create(
                match=match,
                club_member=participant.club_member,
                team=Team.B,
                position=idx
            )

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
        await MatchParticipant.create(
            match=match,
            club_member=male_participants[i].club_member,
            team=Team.A,
            position=1
        )
        await MatchParticipant.create(
            match=match,
            club_member=female_participants[i].club_member,
            team=Team.A,
            position=2
        )

        # 팀 B: 남2 + 여2
        await MatchParticipant.create(
            match=match,
            club_member=male_participants[i+1].club_member,
            team=Team.B,
            position=1
        )
        await MatchParticipant.create(
            match=match,
            club_member=female_participants[i+1].club_member,
            team=Team.B,
            position=2
        )

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
        await MatchParticipant.create(
            match=match,
            club_member=participants[i].club_member,
            team=Team.A,
            position=1
        )

        # 참가자 B
        await MatchParticipant.create(
            match=match,
            club_member=participants[i+1].club_member,
            team=Team.B,
            position=1
        )

        matches.append(match)
        match_number += 1

        court += 1
        if court > num_courts:
            court = 1
            time_slot += 1
            current_datetime = start_datetime + timedelta(minutes=match_duration_minutes * time_slot)

    return matches


def _add_minutes(original_time, minutes: int):
    """
    시간에 분 추가 (하위 호환용)

    주의: 이 함수는 레거시 코드 지원용입니다.
    새 코드에서는 datetime + timedelta를 사용하세요.
    """
    from datetime import datetime as dt, time
    if isinstance(original_time, time):
        base_dt = dt.combine(dt.today(), original_time)
        result_dt = base_dt + timedelta(minutes=minutes)
        return result_dt.time()
    else:
        # datetime인 경우
        return original_time + timedelta(minutes=minutes)
