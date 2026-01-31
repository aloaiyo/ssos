"""
의존성 주입 (HTTP-only 쿠키 기반 인증)

권한 체계:
- 매니저(MANAGER): 모든 권한, 회원/게스트 관리
- 일반 회원(MEMBER): 일정, 경기, 회원 목록 조회
- 게스트(GUEST): 일정과 본인 경기만 조회 (회원 목록 조회 불가)
- 지인(FRIEND): 게스트와 동일한 권한 (전 회원 등 잘 아는 사람)
- 졸업자(ALUMNI): 게스트와 동일한 권한

Note: GUEST, FRIEND, ALUMNI는 동일한 제한된 권한 (exclude_guest로 제외됨)
"""
from fastapi import Depends, HTTPException, status, Request
from app.models.user import User
from app.models.member import ClubMember, MemberRole, MemberStatus
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
    """
    클럽 권한 확인 의존성

    권한 레벨:
    - require_manager=True: 매니저만 접근
    - exclude_guest=True: 매니저/일반회원만 접근 (게스트 제외)
    - 기본: 모든 활성 멤버 접근 (매니저/일반회원/게스트)
    """

    def __init__(
        self,
        require_manager: bool = False,
        exclude_guest: bool = False,
        allow_inactive: bool = False
    ):
        self.require_manager = require_manager
        self.exclude_guest = exclude_guest
        self.allow_inactive = allow_inactive

    async def __call__(
        self,
        club_id: int,
        current_user: User = Depends(get_current_active_user)
    ) -> ClubMember:
        """클럽 멤버십 및 권한 확인"""
        from app.models.club import Club

        # 슈퍼 관리자는 모든 권한
        if current_user.is_super_admin:
            # 클럽 존재 확인
            club = await Club.get_or_none(id=club_id, is_deleted=False)
            if not club:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="동호회를 찾을 수 없습니다"
                )
            # 임시 멤버십 객체 생성 (슈퍼 관리자용)
            membership = await ClubMember.get_or_none(
                club_id=club_id,
                user_id=current_user.id,
                is_deleted=False
            )
            if membership:
                return membership
            # 슈퍼 관리자지만 멤버가 아닌 경우 - 가상 멤버십 반환 불가
            # 실제 멤버십이 필요한 작업에서는 에러 발생

        # 클럽 존재 확인
        club = await Club.get_or_none(id=club_id, is_deleted=False)
        if not club:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="동호회를 찾을 수 없습니다"
            )

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

        # 상태 확인
        if not self.allow_inactive and membership.status != MemberStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="활성 멤버가 아닙니다"
            )

        # 매니저 권한 확인
        if self.require_manager:
            if membership.role != MemberRole.MANAGER:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="클럽 관리자 권한이 필요합니다"
                )

        # 게스트/지인/졸업자 제외 확인 (제한된 권한 역할)
        if self.exclude_guest:
            if membership.role in (MemberRole.GUEST, MemberRole.FRIEND, MemberRole.ALUMNI):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="이 기능에 접근할 수 없습니다"
                )

        return membership


# 편의 의존성
require_club_member = ClubPermission(require_manager=False)
require_club_manager = ClubPermission(require_manager=True)
require_club_member_not_guest = ClubPermission(exclude_guest=True)  # 회원 목록 등 게스트 제외


async def get_club_or_404(club_id: int):
    """클럽 조회 또는 404"""
    from app.models.club import Club
    club = await Club.get_or_none(id=club_id, is_deleted=False)
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="동호회를 찾을 수 없습니다"
        )
    return club
