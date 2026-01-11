"""
공지사항 관련 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.models.user import User
from app.models.club import Club
from app.models.member import ClubMember, MemberRole, MemberStatus
from app.models.announcement import Announcement, AnnouncementType
from app.core.dependencies import get_current_active_user

router = APIRouter(prefix="/clubs/{club_id}/announcements", tags=["공지사항"])


# Schemas
class AnnouncementCreate(BaseModel):
    title: str
    content: str
    announcement_type: str = "general"
    is_pinned: bool = False


class AnnouncementUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    announcement_type: Optional[str] = None
    is_pinned: Optional[bool] = None


class AnnouncementResponse(BaseModel):
    id: int
    title: str
    content: str
    announcement_type: str
    is_pinned: bool
    views: int
    author_id: Optional[int]
    author_name: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


async def check_club_member(club_id: int, user: User) -> ClubMember:
    """클럽 멤버인지 확인"""
    membership = await ClubMember.filter(
        club_id=club_id,
        user=user,
        status=MemberStatus.ACTIVE,
        is_deleted=False
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="동호회 회원만 접근할 수 있습니다."
        )
    return membership


async def check_manager_permission(club_id: int, user: User) -> ClubMember:
    """매니저 권한 확인"""
    membership = await check_club_member(club_id, user)

    if membership.role != MemberRole.MANAGER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다."
        )
    return membership


@router.get("", response_model=List[AnnouncementResponse])
async def get_announcements(
    club_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """공지사항 목록 조회"""
    await check_club_member(club_id, current_user)

    announcements = await Announcement.filter(
        club_id=club_id,
        is_deleted=False
    ).prefetch_related("author").order_by("-is_pinned", "-created_at")

    return [
        AnnouncementResponse(
            id=a.id,
            title=a.title,
            content=a.content,
            announcement_type=a.announcement_type.value,
            is_pinned=a.is_pinned,
            views=a.views,
            author_id=a.author.id if a.author else None,
            author_name=a.author.name if a.author else None,
            created_at=a.created_at,
            updated_at=a.updated_at,
        )
        for a in announcements
    ]


@router.post("", response_model=AnnouncementResponse)
async def create_announcement(
    club_id: int,
    data: AnnouncementCreate,
    current_user: User = Depends(get_current_active_user)
):
    """공지사항 작성"""
    await check_manager_permission(club_id, current_user)

    announcement = await Announcement.create(
        club_id=club_id,
        author=current_user,
        title=data.title,
        content=data.content,
        announcement_type=AnnouncementType(data.announcement_type),
        is_pinned=data.is_pinned,
    )

    return AnnouncementResponse(
        id=announcement.id,
        title=announcement.title,
        content=announcement.content,
        announcement_type=announcement.announcement_type.value,
        is_pinned=announcement.is_pinned,
        views=announcement.views,
        author_id=current_user.id,
        author_name=current_user.name,
        created_at=announcement.created_at,
        updated_at=announcement.updated_at,
    )


@router.get("/{announcement_id}", response_model=AnnouncementResponse)
async def get_announcement(
    club_id: int,
    announcement_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """공지사항 상세 조회"""
    await check_club_member(club_id, current_user)

    announcement = await Announcement.filter(
        id=announcement_id,
        club_id=club_id,
        is_deleted=False
    ).prefetch_related("author").first()

    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="공지사항을 찾을 수 없습니다."
        )

    # 조회수 증가
    announcement.views += 1
    await announcement.save()

    return AnnouncementResponse(
        id=announcement.id,
        title=announcement.title,
        content=announcement.content,
        announcement_type=announcement.announcement_type.value,
        is_pinned=announcement.is_pinned,
        views=announcement.views,
        author_id=announcement.author.id if announcement.author else None,
        author_name=announcement.author.name if announcement.author else None,
        created_at=announcement.created_at,
        updated_at=announcement.updated_at,
    )


@router.put("/{announcement_id}", response_model=AnnouncementResponse)
async def update_announcement(
    club_id: int,
    announcement_id: int,
    data: AnnouncementUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """공지사항 수정"""
    await check_manager_permission(club_id, current_user)

    announcement = await Announcement.filter(
        id=announcement_id,
        club_id=club_id,
        is_deleted=False
    ).prefetch_related("author").first()

    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="공지사항을 찾을 수 없습니다."
        )

    if data.title is not None:
        announcement.title = data.title
    if data.content is not None:
        announcement.content = data.content
    if data.announcement_type is not None:
        announcement.announcement_type = AnnouncementType(data.announcement_type)
    if data.is_pinned is not None:
        announcement.is_pinned = data.is_pinned

    await announcement.save()

    return AnnouncementResponse(
        id=announcement.id,
        title=announcement.title,
        content=announcement.content,
        announcement_type=announcement.announcement_type.value,
        is_pinned=announcement.is_pinned,
        views=announcement.views,
        author_id=announcement.author.id if announcement.author else None,
        author_name=announcement.author.name if announcement.author else None,
        created_at=announcement.created_at,
        updated_at=announcement.updated_at,
    )


@router.delete("/{announcement_id}")
async def delete_announcement(
    club_id: int,
    announcement_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """공지사항 삭제"""
    await check_manager_permission(club_id, current_user)

    announcement = await Announcement.filter(
        id=announcement_id,
        club_id=club_id,
        is_deleted=False
    ).first()

    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="공지사항을 찾을 수 없습니다."
        )

    # Soft delete
    announcement.is_deleted = True
    await announcement.save()

    return {"message": "삭제되었습니다."}
