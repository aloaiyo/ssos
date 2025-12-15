"""
인증 API (HTTP-only 쿠키 + Cognito 이메일 인증)
"""
from fastapi import APIRouter, HTTPException, status, Response, Request, Depends
from app.schemas.user import (
    SignUpRequest,
    VerifyEmailRequest,
    EmailLoginRequest,
    UserResponse,
    UserUpdate,
    Token,
    CognitoCallbackRequest,
)
from app.models.user import User, UserRole, SubscriptionTier
from app.services.cognito_service import CognitoService
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    get_access_token_cookie_settings,
    get_refresh_token_cookie_settings,
)
from app.core.dependencies import get_current_active_user
from app.config import settings

router = APIRouter(prefix="/auth", tags=["인증"])


def set_auth_cookies(response: Response, user_id: int) -> None:
    """인증 쿠키 설정"""
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)

    # HTTP-only 쿠키 설정
    response.set_cookie(
        key="access_token",
        value=access_token,
        **get_access_token_cookie_settings()
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        **get_refresh_token_cookie_settings()
    )


def clear_auth_cookies(response: Response) -> None:
    """인증 쿠키 삭제"""
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")


@router.post("/register", response_model=dict)
async def register(signup_data: SignUpRequest):
    """
    회원가입 (Cognito 이메일 인증번호 발송)

    1. Cognito에 사용자 등록
    2. 이메일로 인증번호 발송
    3. /verify-email로 인증번호 확인 필요
    """
    try:
        # 이메일 중복 체크 (로컬 DB)
        existing = await User.get_or_none(email=signup_data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 사용 중인 이메일입니다"
            )

        # Cognito에 사용자 등록 (인증번호 자동 발송)
        await CognitoService.sign_up(
            email=signup_data.email,
            password=signup_data.password,
            name=signup_data.name
        )

        return {
            "message": "인증번호가 이메일로 발송되었습니다",
            "email": signup_data.email
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/verify-email", response_model=Token)
async def verify_email(verify_data: VerifyEmailRequest, response: Response):
    """
    이메일 인증번호 확인 및 계정 활성화

    성공 시 자동 로그인 (쿠키 설정)
    """
    try:
        # Cognito 이메일 인증
        await CognitoService.confirm_sign_up(
            email=verify_data.email,
            code=verify_data.code
        )

        # Cognito에서 사용자 정보 조회
        cognito_user = await CognitoService.admin_get_user(verify_data.email)
        cognito_sub = cognito_user.get("Username")
        attributes = CognitoService.parse_user_attributes(
            cognito_user.get("UserAttributes", [])
        )

        # 로컬 DB에 사용자 생성
        user = await User.create(
            email=verify_data.email,
            cognito_sub=cognito_sub,
            name=attributes.get("name", verify_data.email.split("@")[0]),
            role=UserRole.USER,
            subscription_tier=SubscriptionTier.FREE,
        )

        # 인증 쿠키 설정
        set_auth_cookies(response, user.id)

        return Token(
            message="회원가입이 완료되었습니다",
            user=UserResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                role=user.role.value,
                subscription_tier=user.subscription_tier.value,
                is_premium=user.is_premium,
                gender=user.gender,
                birth_date=user.birth_date,
                created_at=user.created_at,
            )
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/resend-code", response_model=dict)
async def resend_verification_code(email_data: dict):
    """인증번호 재발송"""
    email = email_data.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이메일을 입력해주세요"
        )

    try:
        await CognitoService.resend_confirmation_code(email)
        return {"message": "인증번호가 재발송되었습니다"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(login_data: EmailLoginRequest, response: Response):
    """
    이메일/비밀번호 로그인

    성공 시 HTTP-only 쿠키에 토큰 설정
    """
    try:
        # Cognito 인증
        auth_result = await CognitoService.admin_initiate_auth(
            email=login_data.email,
            password=login_data.password
        )

        # ID Token에서 cognito_sub 추출
        id_token = auth_result.get("IdToken")
        if not id_token:
            raise ValueError("인증에 실패했습니다")

        claims = await CognitoService.verify_id_token(id_token)
        cognito_sub = claims.get("sub")

        # 로컬 DB에서 사용자 조회
        user = await User.get_or_none(cognito_sub=cognito_sub)
        if not user:
            # 처음 로그인하는 경우 (기존 Cognito 사용자)
            user = await User.create(
                email=login_data.email,
                cognito_sub=cognito_sub,
                name=claims.get("name", login_data.email.split("@")[0]),
                role=UserRole.USER,
                subscription_tier=SubscriptionTier.FREE,
            )

        # 인증 쿠키 설정
        set_auth_cookies(response, user.id)

        return Token(
            message="로그인 성공",
            user=UserResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                role=user.role.value,
                subscription_tier=user.subscription_tier.value,
                is_premium=user.is_premium,
                gender=user.gender,
                birth_date=user.birth_date,
                created_at=user.created_at,
            )
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/logout")
async def logout(response: Response):
    """
    로그아웃 (쿠키 삭제)
    """
    clear_auth_cookies(response)
    return {"message": "로그아웃되었습니다"}


@router.post("/callback", response_model=Token)
async def oauth_callback(callback_data: CognitoCallbackRequest, response: Response):
    """
    OAuth 콜백 처리 (구글 로그인)

    Cognito Authorization Code를 받아서:
    1. Cognito 토큰으로 교환
    2. ID Token 검증
    3. 로컬 사용자 생성/조회
    4. 로컬 JWT 발급 (쿠키)
    """
    import logging
    logger = logging.getLogger(__name__)

    try:
        logger.info(f"OAuth callback received with code: {callback_data.code[:20]}...")

        # 1. Authorization Code를 ID Token으로 교환
        id_token = await CognitoService.exchange_code_for_token(callback_data.code)
        logger.info("ID Token received from Cognito")

        # 2. ID Token 검증 및 claims 추출
        claims = await CognitoService.verify_id_token(id_token)
        cognito_sub = claims.get("sub")
        email = claims.get("email")
        name = claims.get("name") or claims.get("email", "").split("@")[0]

        logger.info(f"Token verified. sub={cognito_sub}, email={email}")

        if not cognito_sub:
            raise ValueError("Cognito sub를 찾을 수 없습니다")

        # 3. 로컬 DB에서 사용자 조회 또는 생성
        user = await User.get_or_none(cognito_sub=cognito_sub)

        if not user:
            # 신규 사용자 생성 (구글 로그인으로 처음 가입)
            logger.info(f"Creating new user: {email}")
            user = await User.create(
                email=email,
                cognito_sub=cognito_sub,
                name=name,
                role=UserRole.USER,
                subscription_tier=SubscriptionTier.FREE,
            )
        else:
            # 기존 사용자: 이메일/이름 업데이트 (변경된 경우)
            if user.email != email or user.name != name:
                user.email = email
                user.name = name
                await user.save()

        # 4. 로컬 JWT 발급 (쿠키 설정)
        set_auth_cookies(response, user.id)
        logger.info(f"Auth cookies set for user: {user.id}")

        return Token(
            message="로그인 성공",
            user=UserResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                role=user.role.value,
                subscription_tier=user.subscription_tier.value,
                is_premium=user.is_premium,
                gender=user.gender,
                birth_date=user.birth_date,
                created_at=user.created_at,
            )
        )

    except ValueError as e:
        logger.error(f"OAuth callback failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in OAuth callback: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OAuth 인증 처리 중 오류가 발생했습니다"
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(request: Request, response: Response):
    """
    토큰 갱신 (쿠키에서 리프레시 토큰 읽기)
    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="리프레시 토큰이 없습니다"
        )

    # 리프레시 토큰 검증
    user_id = verify_refresh_token(refresh_token)
    if user_id is None:
        clear_auth_cookies(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 리프레시 토큰입니다"
        )

    # 사용자 조회
    user = await User.get_or_none(id=user_id, is_deleted=False)
    if not user:
        clear_auth_cookies(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다"
        )

    # 새 토큰 발급
    set_auth_cookies(response, user.id)

    return Token(
        message="토큰이 갱신되었습니다",
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role.value,
            subscription_tier=user.subscription_tier.value,
            is_premium=user.is_premium,
            gender=user.gender,
            birth_date=user.birth_date,
            created_at=user.created_at,
        )
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """현재 사용자 정보 조회"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role.value,
        subscription_tier=current_user.subscription_tier.value,
        is_premium=current_user.is_premium,
        gender=current_user.gender,
        birth_date=current_user.birth_date,
        created_at=current_user.created_at,
    )


@router.put("/me", response_model=UserResponse)
async def update_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """현재 사용자 프로필 수정"""
    update_data = user_update.model_dump(exclude_unset=True)

    if not update_data:
        return UserResponse(
            id=current_user.id,
            email=current_user.email,
            name=current_user.name,
            role=current_user.role.value,
            subscription_tier=current_user.subscription_tier.value,
            is_premium=current_user.is_premium,
            gender=current_user.gender,
            birth_date=current_user.birth_date,
            created_at=current_user.created_at,
        )

    for key, value in update_data.items():
        setattr(current_user, key, value)

    await current_user.save()

    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role.value,
        subscription_tier=current_user.subscription_tier.value,
        is_premium=current_user.is_premium,
        gender=current_user.gender,
        birth_date=current_user.birth_date,
        created_at=current_user.created_at,
    )


@router.get("/check")
async def check_auth(request: Request):
    """
    인증 상태 확인 (프론트엔드용)
    쿠키가 있으면 로그인 상태
    """
    token = request.cookies.get("access_token")
    return {"authenticated": token is not None}
