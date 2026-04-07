"""
공통 페이지네이션 스키마
"""
from typing import Generic, List, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """페이지네이션 응답"""
    items: List[T]
    total: int
    page: int
    page_size: int
    has_next: bool


async def paginate_query(queryset, page: int | None, page_size: int | None, default_page_size: int = 20):
    """
    Tortoise QuerySet에 페이지네이션을 적용한다.

    page가 None이면 모든 항목을 반환 (하위 호환성).
    page가 지정되면 페이지네이션된 결과와 메타데이터를 반환.

    Returns:
        (items, pagination_meta) 튜플
        - items: 조회된 객체 리스트
        - pagination_meta: None (페이지네이션 미적용) 또는 dict (page, page_size, total, has_next)
    """
    if page is None:
        items = await queryset
        return items, None

    if page < 1:
        page = 1
    if page_size is None:
        page_size = default_page_size
    if page_size < 1:
        page_size = 1

    total = await queryset.count()
    offset = (page - 1) * page_size
    items = await queryset.offset(offset).limit(page_size)
    has_next = offset + page_size < total

    return items, {
        "total": total,
        "page": page,
        "page_size": page_size,
        "has_next": has_next,
    }
