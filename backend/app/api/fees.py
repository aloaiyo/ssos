"""
회비 관리 관련 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.models.user import User
from app.models.member import ClubMember, MemberRole, MemberStatus
from app.models.fee import FeeSetting, FeePayment, FeeType, PaymentStatus
from app.core.dependencies import get_current_active_user

router = APIRouter(prefix="/clubs/{club_id}/fees", tags=["회비 관리"])


# Schemas
class FeeSettingCreate(BaseModel):
    name: str
    fee_type: str = "monthly"
    amount: int
    description: Optional[str] = None
    due_day: int = 1


class FeeSettingUpdate(BaseModel):
    name: Optional[str] = None
    fee_type: Optional[str] = None
    amount: Optional[int] = None
    description: Optional[str] = None
    due_day: Optional[int] = None
    is_active: Optional[bool] = None


class FeeSettingResponse(BaseModel):
    id: int
    name: str
    fee_type: str
    amount: int
    description: Optional[str]
    due_day: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentCreate(BaseModel):
    member_id: int
    target_year: int
    target_month: Optional[int] = None
    amount_paid: int
    note: Optional[str] = None


class PaymentUpdate(BaseModel):
    amount_paid: Optional[int] = None
    status: Optional[str] = None
    note: Optional[str] = None


class PaymentResponse(BaseModel):
    id: int
    fee_setting_id: int
    fee_setting_name: str
    member_id: int
    member_name: str
    target_year: int
    target_month: Optional[int]
    amount_due: int
    amount_paid: int
    status: str
    paid_at: Optional[datetime]
    note: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentSummary(BaseModel):
    total_members: int
    paid_count: int
    pending_count: int
    exempt_count: int
    total_due: int
    total_paid: int


async def check_manager_permission(club_id: int, user: User) -> ClubMember:
    """매니저 권한 확인"""
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

    if membership.role != MemberRole.MANAGER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다."
        )
    return membership


# ===== 회비 설정 API =====

@router.get("/settings", response_model=List[FeeSettingResponse])
async def get_fee_settings(
    club_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """회비 설정 목록 조회"""
    await check_manager_permission(club_id, current_user)

    settings = await FeeSetting.filter(club_id=club_id).order_by("-created_at")

    return [
        FeeSettingResponse(
            id=s.id,
            name=s.name,
            fee_type=s.fee_type.value,
            amount=s.amount,
            description=s.description,
            due_day=s.due_day,
            is_active=s.is_active,
            created_at=s.created_at,
        )
        for s in settings
    ]


@router.post("/settings", response_model=FeeSettingResponse)
async def create_fee_setting(
    club_id: int,
    data: FeeSettingCreate,
    current_user: User = Depends(get_current_active_user)
):
    """회비 설정 생성"""
    await check_manager_permission(club_id, current_user)

    setting = await FeeSetting.create(
        club_id=club_id,
        name=data.name,
        fee_type=FeeType(data.fee_type),
        amount=data.amount,
        description=data.description,
        due_day=data.due_day,
    )

    return FeeSettingResponse(
        id=setting.id,
        name=setting.name,
        fee_type=setting.fee_type.value,
        amount=setting.amount,
        description=setting.description,
        due_day=setting.due_day,
        is_active=setting.is_active,
        created_at=setting.created_at,
    )


@router.put("/settings/{setting_id}", response_model=FeeSettingResponse)
async def update_fee_setting(
    club_id: int,
    setting_id: int,
    data: FeeSettingUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """회비 설정 수정"""
    await check_manager_permission(club_id, current_user)

    setting = await FeeSetting.filter(id=setting_id, club_id=club_id).first()
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="회비 설정을 찾을 수 없습니다."
        )

    if data.name is not None:
        setting.name = data.name
    if data.fee_type is not None:
        setting.fee_type = FeeType(data.fee_type)
    if data.amount is not None:
        setting.amount = data.amount
    if data.description is not None:
        setting.description = data.description
    if data.due_day is not None:
        setting.due_day = data.due_day
    if data.is_active is not None:
        setting.is_active = data.is_active

    await setting.save()

    return FeeSettingResponse(
        id=setting.id,
        name=setting.name,
        fee_type=setting.fee_type.value,
        amount=setting.amount,
        description=setting.description,
        due_day=setting.due_day,
        is_active=setting.is_active,
        created_at=setting.created_at,
    )


@router.delete("/settings/{setting_id}")
async def delete_fee_setting(
    club_id: int,
    setting_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """회비 설정 삭제"""
    await check_manager_permission(club_id, current_user)

    deleted_count = await FeeSetting.filter(id=setting_id, club_id=club_id).delete()
    if deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="회비 설정을 찾을 수 없습니다."
        )

    return {"message": "삭제되었습니다."}


# ===== 납부 기록 API =====

@router.get("/payments", response_model=List[PaymentResponse])
async def get_payments(
    club_id: int,
    setting_id: Optional[int] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """납부 기록 조회"""
    await check_manager_permission(club_id, current_user)

    query = FeePayment.filter(fee_setting__club_id=club_id)

    if setting_id:
        query = query.filter(fee_setting_id=setting_id)
    if year:
        query = query.filter(target_year=year)
    if month:
        query = query.filter(target_month=month)
    if status_filter:
        query = query.filter(status=PaymentStatus(status_filter))

    payments = await query.prefetch_related(
        "fee_setting", "club_member", "club_member__user"
    ).order_by("-target_year", "-target_month", "club_member__user__name")

    return [
        PaymentResponse(
            id=p.id,
            fee_setting_id=p.fee_setting.id,
            fee_setting_name=p.fee_setting.name,
            member_id=p.club_member.id,
            member_name=p.club_member.user.name if p.club_member.user else p.club_member.nickname,
            target_year=p.target_year,
            target_month=p.target_month,
            amount_due=p.amount_due,
            amount_paid=p.amount_paid,
            status=p.status.value,
            paid_at=p.paid_at,
            note=p.note,
            created_at=p.created_at,
        )
        for p in payments
    ]


@router.post("/payments/generate")
async def generate_payments(
    club_id: int,
    setting_id: int,
    year: int,
    month: Optional[int] = None,
    current_user: User = Depends(get_current_active_user)
):
    """월별 납부 기록 일괄 생성"""
    await check_manager_permission(club_id, current_user)

    setting = await FeeSetting.filter(id=setting_id, club_id=club_id).first()
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="회비 설정을 찾을 수 없습니다."
        )

    # 활성 회원 조회
    members = await ClubMember.filter(
        club_id=club_id,
        status=MemberStatus.ACTIVE
    )

    created_count = 0
    for member in members:
        # 이미 존재하는지 확인
        existing = await FeePayment.filter(
            fee_setting=setting,
            club_member=member,
            target_year=year,
            target_month=month
        ).first()

        if not existing:
            await FeePayment.create(
                fee_setting=setting,
                club_member=member,
                target_year=year,
                target_month=month,
                amount_due=setting.amount,
                recorded_by=current_user,
            )
            created_count += 1

    return {
        "message": f"{created_count}명의 납부 기록이 생성되었습니다.",
        "created_count": created_count
    }


@router.put("/payments/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    club_id: int,
    payment_id: int,
    data: PaymentUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """납부 기록 수정"""
    await check_manager_permission(club_id, current_user)

    payment = await FeePayment.filter(
        id=payment_id,
        fee_setting__club_id=club_id
    ).prefetch_related("fee_setting", "club_member", "club_member__user").first()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="납부 기록을 찾을 수 없습니다."
        )

    if data.amount_paid is not None:
        payment.amount_paid = data.amount_paid
        # 자동 상태 업데이트
        if payment.amount_paid >= payment.amount_due:
            payment.status = PaymentStatus.PAID
            payment.paid_at = datetime.utcnow()
        elif payment.amount_paid > 0:
            payment.status = PaymentStatus.PARTIAL
        else:
            payment.status = PaymentStatus.PENDING

    if data.status is not None:
        payment.status = PaymentStatus(data.status)
        if payment.status == PaymentStatus.PAID and not payment.paid_at:
            payment.paid_at = datetime.utcnow()

    if data.note is not None:
        payment.note = data.note

    payment.recorded_by = current_user
    await payment.save()

    return PaymentResponse(
        id=payment.id,
        fee_setting_id=payment.fee_setting.id,
        fee_setting_name=payment.fee_setting.name,
        member_id=payment.club_member.id,
        member_name=payment.club_member.user.name if payment.club_member.user else payment.club_member.nickname,
        target_year=payment.target_year,
        target_month=payment.target_month,
        amount_due=payment.amount_due,
        amount_paid=payment.amount_paid,
        status=payment.status.value,
        paid_at=payment.paid_at,
        note=payment.note,
        created_at=payment.created_at,
    )


@router.get("/summary", response_model=PaymentSummary)
async def get_payment_summary(
    club_id: int,
    setting_id: int,
    year: int,
    month: Optional[int] = None,
    current_user: User = Depends(get_current_active_user)
):
    """납부 현황 요약"""
    await check_manager_permission(club_id, current_user)

    query = FeePayment.filter(
        fee_setting_id=setting_id,
        fee_setting__club_id=club_id,
        target_year=year
    )
    if month:
        query = query.filter(target_month=month)

    payments = await query.all()

    total_members = len(payments)
    paid_count = sum(1 for p in payments if p.status == PaymentStatus.PAID)
    pending_count = sum(1 for p in payments if p.status == PaymentStatus.PENDING)
    exempt_count = sum(1 for p in payments if p.status == PaymentStatus.EXEMPT)
    total_due = sum(p.amount_due for p in payments)
    total_paid = sum(p.amount_paid for p in payments)

    return PaymentSummary(
        total_members=total_members,
        paid_count=paid_count,
        pending_count=pending_count,
        exempt_count=exempt_count,
        total_due=total_due,
        total_paid=total_paid,
    )
