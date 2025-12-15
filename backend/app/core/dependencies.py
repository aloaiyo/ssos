"""
의존성 주입 (HTTP-only 쿠키 기반 인증)
"""
from fastapi import Depends, HTTPException, status, Request
from app.models.user import User
from app.models.member import ClubMember, MemberRole
from app.core.security import verify_access_token


async def get_current_user(request: Request) -> User:
    """
    현재 인증된 사용자 조회 (HTTP-only 쿠키에서 토큰 읽기)
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증이 필요합니다",
    )

    # 쿠키에서 액세스 토큰 읽기
    token = request.cookies.get("access_token")
    if not token:
        raise credentials_exception

    # 토큰 검증
    user_id = verify_access_token(token)
    if user_id is None:
        raise credentials_exception

    # 사용자 조회
    user = await User.get_or_none(id=user_id, is_deleted=False)
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """현재 활성 사용자 (삭제되지 않은 사용자)"""
    if current_user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비활성화된 계정입니다"
        )
    return current_user


async def get_optional_user(request: Request) -> User | None:
    """
    선택적 사용자 조회 (로그인하지 않아도 됨)
    """
    token = request.cookies.get("access_token")
    if not token:
        return None

    user_id = verify_access_token(token)
    if user_id is None:
        return None

    user = await User.get_or_none(id=user_id, is_deleted=False)
    return user


async def require_super_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """슈퍼 관리자 권한 확인"""
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )
    return current_user


# 기존 호환성을 위한 별칭
get_current_admin_user = require_super_admin


class ClubPermission:
    """클럽 권한 확인 의존성"""

    def __init__(self, require_manager: bool = False):
        self.require_manager = require_manager

    async def __call__(
        self,
        club_id: int,
        current_user: User = Depends(get_current_active_user)
    ) -> ClubMember:
        """클럽 멤버십 및 권한 확인"""
        membership = await ClubMember.get_or_none(
            club_id=club_id,
            user_id=current_user.id,
            is_deleted=False
        )

        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="클럽 멤버가 아닙니다"
            )

        if self.require_manager and membership.role != MemberRole.MANAGER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="클럽 관리자 권한이 필요합니다"
            )

        return membership


# 편의 의존성
require_club_member = ClubPermission(require_manager=False)
require_club_manager = ClubPermission(require_manager=True)
