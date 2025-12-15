"""
인증 서비스 (Cognito Hosted UI 통합)
"""
from typing import Optional
from app.models.user import User
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.services.cognito_service import CognitoService
from datetime import timedelta
from app.config import settings


async def sync_user_from_cognito_code(code: str) -> User:
    """
    Cognito Authorization Code를 ID Token으로 교환하고 사용자 정보 동기화
    
    Args:
        code: Cognito Authorization Code
        
    Returns:
        User 객체
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Authorization Code를 ID Token으로 교환
    logger.info("토큰 교환 시작")
    id_token = await CognitoService.exchange_code_for_token(code)
    logger.info("토큰 교환 완료")
    
    # ID Token 검증 및 디코딩
    logger.info("토큰 검증 시작")
    claims = await CognitoService.verify_id_token(id_token)
    logger.info("토큰 검증 완료")
    
    # Cognito Sub 추출
    cognito_sub = claims.get('sub')
    if not cognito_sub:
        raise ValueError('토큰에서 사용자 정보를 찾을 수 없습니다')
    
    # 사용자 정보 추출
    email = claims.get('email', '')
    name = claims.get('name', '') or claims.get('given_name', '') or email.split('@')[0] if email else ''
    
    # 로컬 DB에서 사용자 조회 또는 생성
    logger.info(f"사용자 조회/생성: cognito_sub={cognito_sub}")
    user = await User.get_or_none(cognito_sub=cognito_sub)
    
    if not user:
        # 이메일로도 확인 (마이그레이션용)
        if email:
            user = await User.get_or_none(email=email)
            if user:
                # 기존 사용자에 cognito_sub 추가
                user.cognito_sub = cognito_sub
                if not user.name or user.name == user.email:
                    user.name = name
                await user.save()
        
        if not user:
            # 새 사용자 생성
            user = await User.create(
                email=email if email else None,
                cognito_sub=cognito_sub,
                name=name,
            )
            logger.info(f"새 사용자 생성: user_id={user.id}")
    else:
        # 기존 사용자 정보 업데이트 (Cognito에서 최신 정보 반영)
        if email and user.email != email:
            user.email = email
        if name and user.name != name:
            user.name = name
        await user.save()
        logger.info(f"기존 사용자 업데이트: user_id={user.id}")
    
    return user


from app.core.security import create_access_token, create_refresh_token, verify_token

# ... (existing imports)


def create_user_token(user_id: int) -> dict:
    """사용자 토큰 생성 (Access + Refresh)"""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user_id)}, expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(
        data={"sub": str(user_id)}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


async def refresh_access_token(refresh_token: str) -> dict:
    """리프레시 토큰으로 액세스 토큰 갱신"""
    payload = verify_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise ValueError("유효하지 않은 리프레시 토큰입니다")
        
    user_id = payload.get("sub")
    if not user_id:
        raise ValueError("토큰에서 사용자 정보를 찾을 수 없습니다")
        
    # 사용자 존재 여부 확인
    user = await User.get_or_none(id=int(user_id))
    if not user:
        raise ValueError("사용자를 찾을 수 없습니다")
        
    # 새 액세스 토큰 생성
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user_id)}, expires_delta=access_token_expires
    )
    
    # 리프레시 토큰은 그대로 반환 (또는 로테이션 정책 적용 가능)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
