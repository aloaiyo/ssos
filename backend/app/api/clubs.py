"""
동호회 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.club import ClubCreate, ClubResponse, ClubUpdate, ClubSearchResponse
from app.schemas.schedule import ScheduleResponse
from app.models.club import Club
from app.models.schedule import ClubSchedule
from app.models.user import User
from app.core.dependencies import get_current_active_user

router = APIRouter(prefix="/clubs", tags=["동호회"])


async def get_club_with_schedules(club: Club) -> dict:
    """Club을 schedules와 함께 dict로 변환"""
    schedules = await ClubSchedule.filter(club=club, is_deleted=False).order_by("day_of_week", "start_time")
    club_dict = {
        "id": club.id,
        "name": club.name,
        "description": club.description,
        "created_by_id": club.created_by_id,
        "created_at": club.created_at,
        "modified_at": club.modified_at,
        "is_deleted": club.is_deleted,
        "default_num_courts": club.default_num_courts,
        "default_match_duration": club.default_match_duration,
        "default_break_duration": club.default_break_duration,
        "default_warmup_duration": club.default_warmup_duration,
        "location": club.location,
        "is_join_allowed": club.is_join_allowed,
        "requires_approval": club.requires_approval,
        "schedules": [ScheduleResponse.model_validate(s) for s in schedules],
    }
    return club_dict


@router.get("", response_model=List[ClubSearchResponse])
async def list_clubs(
    current_user: User = Depends(get_current_active_user),
    search: str = None,
    skip: int = 0,
    limit: int = 20
):
    """
    동호회 목록 조회
    - 기본: 최근 생성된 20개 동호회
    - 검색: 이름에 검색어가 포함된 동호회
    - 회원수와 내 가입 상태 포함
    """
    from app.models.member import ClubMember, MemberStatus

    query = Club.filter(is_deleted=False)
    if search:
        query = query.filter(name__icontains=search)

    # 최신순 정렬
    clubs = await query.order_by("-created_at").offset(skip).limit(limit)

    result = []
    for club in clubs:
        # 활성 회원수 조회
        member_count = await ClubMember.filter(
            club=club,
            status=MemberStatus.ACTIVE,
            is_deleted=False
        ).count()

        # 내 가입 상태 조회
        my_membership = await ClubMember.get_or_none(
            club=club,
            user=current_user,
            is_deleted=False
        )
        my_status = my_membership.status.value if my_membership else None

        result.append(ClubSearchResponse(
            id=club.id,
            name=club.name,
            description=club.description,
            created_at=club.created_at,
            location=club.location,
            is_join_allowed=club.is_join_allowed,
            requires_approval=club.requires_approval,
            member_count=member_count,
            my_status=my_status
        ))

    return result


@router.post("", response_model=ClubResponse, status_code=status.HTTP_201_CREATED)
async def create_club(
    club_data: ClubCreate,
    current_user: User = Depends(get_current_active_user)
):
    """동호회 생성"""
    # 동호회 생성 (기본 정보 포함)
    club = await Club.create(
        name=club_data.name,
        description=club_data.description,
        created_by=current_user,
        # 기본 정보
        default_num_courts=club_data.default_num_courts,
        default_match_duration=club_data.default_match_duration,
        location=club_data.location,
    )

    # 정기 활동 스케줄 생성
    if club_data.schedules:
        for schedule in club_data.schedules:
            await ClubSchedule.create(
                club=club,
                day_of_week=schedule.day_of_week,
                start_time=schedule.start_time,
                end_time=schedule.end_time,
                is_active=schedule.is_active,
            )

    # 생성자를 관리자로 추가
    from app.models.member import ClubMember, MemberRole, MemberStatus, Gender

    # 사용자 성별을 ClubMember 성별로 변환
    if current_user.gender == 'male':
        gender = Gender.MALE
    elif current_user.gender == 'female':
        gender = Gender.FEMALE
    else:
        gender = Gender.MALE  # 기본값

    await ClubMember.create(
        club=club,
        user=current_user,
        role=MemberRole.MANAGER,  # 생성자를 매니저로 설정
        status=MemberStatus.ACTIVE,
        gender=gender,
    )

    return ClubResponse.model_validate(await get_club_with_schedules(club))


@router.post("/{club_id}/join", status_code=status.HTTP_201_CREATED)
async def join_club(
    club_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """동호회 가입 요청"""
    club = await Club.get_or_none(id=club_id, is_deleted=False)
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="동호회를 찾을 수 없습니다"
        )

    # 가입 허용 여부 확인
    if not club.is_join_allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 동호회는 현재 가입을 받지 않습니다"
        )

    from app.models.member import ClubMember, MemberRole, MemberStatus, Gender

    # 이미 가입되어 있는지 확인
    existing_member = await ClubMember.get_or_none(club=club, user=current_user)

    if existing_member:
        if existing_member.status == MemberStatus.BANNED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="이 동호회에서 추방되었습니다."
            )
        elif existing_member.status == MemberStatus.LEFT:
            # 재가입 요청
            if club.requires_approval:
                existing_member.status = MemberStatus.PENDING
                existing_member.role = MemberRole.MEMBER
                await existing_member.save()
                return {"message": "재가입 요청이 완료되었습니다. 관리자의 승인을 기다려주세요."}
            else:
                existing_member.status = MemberStatus.ACTIVE
                existing_member.role = MemberRole.MEMBER
                await existing_member.save()
                return {"message": "재가입이 완료되었습니다."}
        elif existing_member.status in [MemberStatus.ACTIVE, MemberStatus.PENDING]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 가입된 동호회입니다"
            )

    # 사용자 성별을 ClubMember 성별로 변환
    if current_user.gender == 'male':
        gender = Gender.MALE
    elif current_user.gender == 'female':
        gender = Gender.FEMALE
    else:
        gender = Gender.MALE  # 기본값

    # 승인 필요 여부에 따라 상태 결정
    initial_status = MemberStatus.PENDING if club.requires_approval else MemberStatus.ACTIVE

    await ClubMember.create(
        club=club,
        user=current_user,
        role=MemberRole.MEMBER,
        status=initial_status,
        gender=gender,
    )

    if club.requires_approval:
        return {"message": "가입 요청이 완료되었습니다. 관리자의 승인을 기다려주세요."}
    return {"message": "가입이 완료되었습니다"}


@router.post("/{club_id}/leave", status_code=status.HTTP_200_OK)
async def leave_club(
    club_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """동호회 탈퇴"""
    club = await Club.get_or_none(id=club_id, is_deleted=False)
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="동호회를 찾을 수 없습니다"
        )
        
    from app.models.member import ClubMember, MemberStatus
    
    member = await ClubMember.get_or_none(club=club, user=current_user)
    if not member or member.status != MemberStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="활동 중인 회원이 아닙니다"
        )
        
    member.status = MemberStatus.LEFT
    await member.save()
    
    return {"message": "동호회를 탈퇴했습니다"}


@router.post("/{club_id}/approve", status_code=status.HTTP_200_OK)
async def approve_member(
    club_id: int,
    user_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """회원 가입 승인 (재가입 등)"""
    club = await Club.get_or_none(id=club_id, is_deleted=False)
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="동호회를 찾을 수 없습니다"
        )
        
    from app.models.member import ClubMember, MemberRole, MemberStatus

    # 요청자가 매니저인지 확인
    requester = await ClubMember.get_or_none(club=club, user=current_user, is_deleted=False)
    if not requester or requester.role != MemberRole.MANAGER or requester.status != MemberStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없습니다"
        )
        
    # 대상 회원 조회
    target_member = await ClubMember.get_or_none(club=club, user_id=user_id)
    if not target_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="회원을 찾을 수 없습니다"
        )
        
    if target_member.status != MemberStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="승인 대기 중인 회원이 아닙니다"
        )
        
    target_member.status = MemberStatus.ACTIVE
    await target_member.save()
    
    return {"message": "회원 가입을 승인했습니다"}


@router.get("/{club_id}", response_model=ClubResponse)
async def get_club(
    club_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """동호회 상세 조회"""
    club = await Club.get_or_none(id=club_id, is_deleted=False)
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="동호회를 찾을 수 없습니다"
        )
    return ClubResponse.model_validate(await get_club_with_schedules(club))


@router.put("/{club_id}", response_model=ClubResponse)
async def update_club(
    club_id: int,
    club_data: ClubUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """동호회 수정"""
    club = await Club.get_or_none(id=club_id, is_deleted=False)
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="동호회를 찾을 수 없습니다"
        )

    # 권한 확인: 매니저만 수정 가능
    from app.models.member import ClubMember, MemberRole, MemberStatus
    requester = await ClubMember.get_or_none(
        club=club, user=current_user, is_deleted=False
    )
    if not requester or requester.role != MemberRole.MANAGER or requester.status != MemberStatus.ACTIVE:
        if not current_user.is_super_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="동호회를 수정할 권한이 없습니다"
            )

    # 기본 정보 수정
    if club_data.name is not None:
        club.name = club_data.name
    if club_data.description is not None:
        club.description = club_data.description
    if club_data.default_num_courts is not None:
        club.default_num_courts = club_data.default_num_courts
    if club_data.default_match_duration is not None:
        club.default_match_duration = club_data.default_match_duration
    if club_data.default_break_duration is not None:
        club.default_break_duration = club_data.default_break_duration
    if club_data.default_warmup_duration is not None:
        club.default_warmup_duration = club_data.default_warmup_duration
    if club_data.location is not None:
        club.location = club_data.location
    # 가입 설정 수정
    if club_data.is_join_allowed is not None:
        club.is_join_allowed = club_data.is_join_allowed
    if club_data.requires_approval is not None:
        club.requires_approval = club_data.requires_approval

    await club.save()

    # 스케줄 업데이트 (전체 교체 방식)
    if club_data.schedules is not None:
        # 기존 스케줄 soft delete
        await ClubSchedule.filter(club=club).update(is_deleted=True)

        # 새 스케줄 생성
        for schedule in club_data.schedules:
            await ClubSchedule.create(
                club=club,
                day_of_week=schedule.day_of_week,
                start_time=schedule.start_time,
                end_time=schedule.end_time,
                is_active=schedule.is_active,
            )

    return ClubResponse.model_validate(await get_club_with_schedules(club))


@router.delete("/{club_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_club(
    club_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """동호회 삭제 (soft delete)"""
    club = await Club.get_or_none(id=club_id, is_deleted=False)
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="동호회를 찾을 수 없습니다"
        )

    # 권한 확인: 매니저만 삭제 가능
    from app.models.member import ClubMember, MemberRole, MemberStatus
    requester = await ClubMember.get_or_none(
        club=club, user=current_user, is_deleted=False
    )
    if not requester or requester.role != MemberRole.MANAGER or requester.status != MemberStatus.ACTIVE:
        if not current_user.is_super_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="동호회를 삭제할 권한이 없습니다"
            )

    # Soft delete
    club.is_deleted = True
    await club.save()
