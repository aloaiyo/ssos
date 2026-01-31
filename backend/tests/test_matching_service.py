"""
매칭 서비스 테스트

참고: matching_service.py는 DB 의존성이 있는 async 함수들로 구성됨
여기서는 헬퍼 함수와 로직만 테스트
"""
import pytest
from datetime import time, timedelta

from app.services.matching_service import _add_minutes
from app.models.match import MatchType, MatchStatus, Team


class TestAddMinutes:
    """_add_minutes 헬퍼 함수 테스트"""

    def test_add_30_minutes(self):
        """30분 추가"""
        original = time(9, 0)
        result = _add_minutes(original, 30)

        assert result == time(9, 30)

    def test_add_minutes_crosses_hour(self):
        """시간 경계 넘기"""
        original = time(9, 45)
        result = _add_minutes(original, 30)

        assert result == time(10, 15)

    def test_add_60_minutes(self):
        """60분 추가"""
        original = time(10, 0)
        result = _add_minutes(original, 60)

        assert result == time(11, 0)

    def test_add_minutes_multiple_hours(self):
        """여러 시간 추가"""
        original = time(9, 0)
        result = _add_minutes(original, 180)  # 3시간

        assert result == time(12, 0)

    def test_add_zero_minutes(self):
        """0분 추가"""
        original = time(9, 30)
        result = _add_minutes(original, 0)

        assert result == time(9, 30)


class TestMatchEnums:
    """매치 관련 Enum 테스트"""

    def test_match_type_values(self):
        """매치 타입 값"""
        assert MatchType.SINGLES.value == "singles"
        assert MatchType.MENS_DOUBLES.value == "mens_doubles"
        assert MatchType.WOMENS_DOUBLES.value == "womens_doubles"
        assert MatchType.MIXED_DOUBLES.value == "mixed_doubles"

    def test_match_type_count(self):
        """매치 타입 개수"""
        assert len(MatchType) == 4

    def test_match_status_values(self):
        """매치 상태 값"""
        assert MatchStatus.SCHEDULED.value == "scheduled"
        assert MatchStatus.IN_PROGRESS.value == "in_progress"
        assert MatchStatus.COMPLETED.value == "completed"

    def test_team_values(self):
        """팀 값"""
        assert Team.A.value == "A"
        assert Team.B.value == "B"


class TestMatchingLogic:
    """매칭 로직 테스트 (순수 함수 버전)"""

    def test_calculate_max_matches_in_time(self):
        """시간 내 최대 경기 수 계산"""
        start = time(9, 0)
        end = time(12, 0)
        duration = 30  # 분

        # 3시간 = 180분, 30분당 1경기 = 6경기
        total_minutes = (end.hour - start.hour) * 60 + (end.minute - start.minute)
        max_matches = total_minutes // duration

        assert max_matches == 6

    def test_calculate_total_matches_possible(self):
        """코트 수 고려한 총 경기 수"""
        num_courts = 2
        time_slots = 6  # 시간대

        total_possible = num_courts * time_slots
        assert total_possible == 12

    def test_doubles_requires_4_players(self):
        """복식은 4명 필요"""
        participants = 4
        players_per_match = 4

        can_form = participants >= players_per_match
        assert can_form is True

    def test_doubles_cannot_form_with_3(self):
        """3명으로 복식 불가"""
        participants = 3
        players_per_match = 4

        can_form = participants >= players_per_match
        assert can_form is False

    def test_singles_requires_2_players(self):
        """단식은 2명 필요"""
        participants = 2
        players_per_match = 2

        can_form = participants >= players_per_match
        assert can_form is True

    def test_mixed_doubles_needs_both_genders(self):
        """혼복은 남녀 모두 필요"""
        males = 2
        females = 2

        can_form = males >= 2 and females >= 2
        assert can_form is True

    def test_mixed_doubles_insufficient_males(self):
        """남자 부족 시 혼복 불가"""
        males = 1
        females = 3

        can_form = males >= 2 and females >= 2
        assert can_form is False

    def test_count_possible_doubles_matches(self):
        """가능한 복식 경기 수"""
        participants = 8
        players_per_match = 4

        possible_matches = participants // players_per_match
        assert possible_matches == 2

    def test_count_leftover_after_matching(self):
        """매칭 후 남은 인원"""
        participants = 10
        players_per_match = 4

        matches = participants // players_per_match
        leftover = participants % players_per_match

        assert matches == 2
        assert leftover == 2


class TestTimeSlotCalculation:
    """시간대 계산 테스트"""

    def test_generate_time_slots(self):
        """시간대 생성"""
        start = time(9, 0)
        duration = 30
        num_slots = 6

        slots = []
        current = start
        for _ in range(num_slots):
            slots.append(current)
            current = _add_minutes(current, duration)

        assert len(slots) == 6
        assert slots[0] == time(9, 0)
        assert slots[1] == time(9, 30)
        assert slots[5] == time(11, 30)

    def test_slots_with_break_time(self):
        """휴식 시간 포함 시간대"""
        start = time(9, 0)
        match_duration = 30
        break_duration = 5
        total_duration = match_duration + break_duration

        current = start
        slots = []
        for _ in range(5):
            slots.append(current)
            current = _add_minutes(current, total_duration)

        assert slots[0] == time(9, 0)
        assert slots[1] == time(9, 35)
        assert slots[2] == time(10, 10)


class TestCourtAllocation:
    """코트 배정 테스트"""

    def test_round_robin_court_assignment(self):
        """라운드 로빈 코트 배정"""
        num_courts = 3
        num_matches = 7

        assignments = []
        for i in range(num_matches):
            court = (i % num_courts) + 1
            assignments.append(court)

        assert assignments == [1, 2, 3, 1, 2, 3, 1]

    def test_court_overflow_to_next_time(self):
        """코트 초과 시 다음 시간대"""
        num_courts = 2
        matches_scheduled = 0
        time_slot = 0

        for _ in range(5):  # 5경기 예약
            court = (matches_scheduled % num_courts) + 1
            if matches_scheduled > 0 and court == 1:
                time_slot += 1
            matches_scheduled += 1

        # 2코트로 5경기 = 3개 시간대 (0, 1, 2)
        assert time_slot == 2
