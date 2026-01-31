"""
타임존 유틸리티

UTC로 저장하고 KST(Asia/Seoul)로 응답하는 패턴 지원
"""
from datetime import datetime, timezone, timedelta
from typing import Optional, Any, Annotated
from functools import lru_cache

from pydantic import BeforeValidator, PlainSerializer


# 한국 표준시 (KST = UTC+9)
KST = timezone(timedelta(hours=9))


def utc_now() -> datetime:
    """현재 UTC 시간 반환 (timezone-aware)"""
    return datetime.now(timezone.utc)


def to_utc(dt: datetime) -> datetime:
    """
    datetime을 UTC로 변환

    - naive datetime은 KST로 가정하고 UTC로 변환
    - aware datetime은 UTC로 변환
    """
    if dt is None:
        return None

    if dt.tzinfo is None:
        # naive datetime은 KST로 가정
        dt = dt.replace(tzinfo=KST)

    return dt.astimezone(timezone.utc)


def to_kst(dt: datetime) -> datetime:
    """
    datetime을 KST로 변환

    - naive datetime은 UTC로 가정하고 KST로 변환
    - aware datetime은 KST로 변환
    """
    if dt is None:
        return None

    if dt.tzinfo is None:
        # naive datetime은 UTC로 가정
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(KST)


def parse_kst_datetime(value: Any) -> datetime:
    """
    입력값을 파싱하여 UTC datetime으로 변환

    - 문자열: ISO 8601 파싱 후 KST로 가정하여 UTC 변환
    - datetime: KST로 가정하여 UTC 변환 (naive인 경우)
    """
    if value is None:
        return None

    if isinstance(value, datetime):
        return to_utc(value)

    if isinstance(value, str):
        # ISO 8601 파싱
        try:
            # "Z" 접미사 처리
            if value.endswith("Z"):
                value = value[:-1] + "+00:00"

            dt = datetime.fromisoformat(value)

            if dt.tzinfo is None:
                # naive는 KST로 가정
                dt = dt.replace(tzinfo=KST)

            return dt.astimezone(timezone.utc)
        except ValueError:
            raise ValueError(f"Invalid datetime format: {value}")

    raise ValueError(f"Cannot parse datetime from: {type(value)}")


def serialize_to_kst(dt: datetime) -> str:
    """datetime을 KST ISO 8601 문자열로 직렬화"""
    if dt is None:
        return None

    kst_dt = to_kst(dt)
    return kst_dt.isoformat()


# Pydantic용 타입 어노테이션
# 요청: KST 입력 → UTC 저장
# 응답: UTC → KST 출력
KSTDatetime = Annotated[
    datetime,
    BeforeValidator(parse_kst_datetime),
    PlainSerializer(serialize_to_kst, return_type=str)
]


# Optional 버전
def parse_optional_kst_datetime(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    return parse_kst_datetime(value)


def serialize_optional_to_kst(dt: Optional[datetime]) -> Optional[str]:
    if dt is None:
        return None
    return serialize_to_kst(dt)


OptionalKSTDatetime = Annotated[
    Optional[datetime],
    BeforeValidator(parse_optional_kst_datetime),
    PlainSerializer(serialize_optional_to_kst, return_type=Optional[str])
]
