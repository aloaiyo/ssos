"""
타임존 유틸리티 테스트
"""
import pytest
from datetime import datetime, timezone, timedelta

from app.core.timezone import (
    KST,
    utc_now,
    to_utc,
    to_kst,
    parse_kst_datetime,
    serialize_to_kst,
)


class TestUtcNow:
    """utc_now() 테스트"""

    def test_returns_timezone_aware_datetime(self):
        """timezone-aware datetime 반환"""
        result = utc_now()
        assert result.tzinfo is not None
        assert result.tzinfo == timezone.utc

    def test_returns_current_time(self):
        """현재 시간 반환"""
        before = datetime.now(timezone.utc)
        result = utc_now()
        after = datetime.now(timezone.utc)

        assert before <= result <= after


class TestToUtc:
    """to_utc() 테스트"""

    def test_naive_datetime_assumed_kst(self):
        """naive datetime은 KST로 가정하고 UTC로 변환"""
        # KST 2026-01-31 18:00:00 → UTC 2026-01-31 09:00:00
        naive_kst = datetime(2026, 1, 31, 18, 0, 0)
        result = to_utc(naive_kst)

        assert result.tzinfo == timezone.utc
        assert result.hour == 9  # 18 - 9 = 9

    def test_aware_datetime_converted(self):
        """aware datetime은 UTC로 변환"""
        aware_kst = datetime(2026, 1, 31, 18, 0, 0, tzinfo=KST)
        result = to_utc(aware_kst)

        assert result.tzinfo == timezone.utc
        assert result.hour == 9

    def test_utc_datetime_unchanged(self):
        """UTC datetime은 그대로 유지"""
        utc_dt = datetime(2026, 1, 31, 9, 0, 0, tzinfo=timezone.utc)
        result = to_utc(utc_dt)

        assert result.hour == 9

    def test_none_returns_none(self):
        """None 입력 시 None 반환"""
        assert to_utc(None) is None


class TestToKst:
    """to_kst() 테스트"""

    def test_naive_datetime_assumed_utc(self):
        """naive datetime은 UTC로 가정하고 KST로 변환"""
        # UTC 2026-01-31 09:00:00 → KST 2026-01-31 18:00:00
        naive_utc = datetime(2026, 1, 31, 9, 0, 0)
        result = to_kst(naive_utc)

        assert result.tzinfo == KST
        assert result.hour == 18  # 9 + 9 = 18

    def test_aware_utc_converted_to_kst(self):
        """UTC aware datetime을 KST로 변환"""
        utc_dt = datetime(2026, 1, 31, 9, 0, 0, tzinfo=timezone.utc)
        result = to_kst(utc_dt)

        assert result.tzinfo == KST
        assert result.hour == 18

    def test_kst_datetime_unchanged(self):
        """KST datetime은 그대로 유지"""
        kst_dt = datetime(2026, 1, 31, 18, 0, 0, tzinfo=KST)
        result = to_kst(kst_dt)

        assert result.hour == 18

    def test_none_returns_none(self):
        """None 입력 시 None 반환"""
        assert to_kst(None) is None


class TestParseKstDatetime:
    """parse_kst_datetime() 테스트"""

    def test_iso_string_without_timezone(self):
        """타임존 없는 ISO 문자열은 KST로 해석"""
        result = parse_kst_datetime("2026-01-31T18:00:00")

        assert result.tzinfo == timezone.utc
        assert result.hour == 9  # KST 18시 → UTC 9시

    def test_iso_string_with_z_suffix(self):
        """Z 접미사는 UTC로 해석"""
        result = parse_kst_datetime("2026-01-31T09:00:00Z")

        assert result.tzinfo == timezone.utc
        assert result.hour == 9

    def test_iso_string_with_offset(self):
        """오프셋 포함 문자열 파싱"""
        result = parse_kst_datetime("2026-01-31T18:00:00+09:00")

        assert result.tzinfo == timezone.utc
        assert result.hour == 9

    def test_datetime_object_converted(self):
        """datetime 객체도 처리"""
        dt = datetime(2026, 1, 31, 18, 0, 0)  # naive, KST로 가정
        result = parse_kst_datetime(dt)

        assert result.tzinfo == timezone.utc
        assert result.hour == 9

    def test_none_returns_none(self):
        """None 입력 시 None 반환"""
        assert parse_kst_datetime(None) is None

    def test_invalid_string_raises_error(self):
        """잘못된 문자열은 ValueError"""
        with pytest.raises(ValueError):
            parse_kst_datetime("invalid-date")


class TestSerializeToKst:
    """serialize_to_kst() 테스트"""

    def test_utc_datetime_to_kst_string(self):
        """UTC datetime을 KST ISO 문자열로 직렬화"""
        utc_dt = datetime(2026, 1, 31, 9, 0, 0, tzinfo=timezone.utc)
        result = serialize_to_kst(utc_dt)

        assert "2026-01-31T18:00:00" in result
        assert "+09:00" in result

    def test_naive_datetime_assumed_utc(self):
        """naive datetime은 UTC로 가정"""
        naive_dt = datetime(2026, 1, 31, 9, 0, 0)
        result = serialize_to_kst(naive_dt)

        assert "2026-01-31T18:00:00" in result

    def test_none_returns_none(self):
        """None 입력 시 None 반환"""
        assert serialize_to_kst(None) is None

    def test_output_is_iso_format(self):
        """출력이 ISO 8601 형식"""
        dt = datetime(2026, 1, 31, 9, 30, 45, tzinfo=timezone.utc)
        result = serialize_to_kst(dt)

        # ISO 형식 검증
        assert "T" in result
        assert ":" in result


class TestKstTimezone:
    """KST 타임존 상수 테스트"""

    def test_kst_offset_is_9_hours(self):
        """KST는 UTC+9"""
        assert KST.utcoffset(None) == timedelta(hours=9)

    def test_kst_name(self):
        """KST 이름 확인"""
        # timedelta 기반 timezone은 이름이 UTC+09:00 형식
        assert "09:00" in str(KST)
