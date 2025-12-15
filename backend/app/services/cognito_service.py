"""
AWS Cognito 서비스
"""
import boto3
import asyncio
from functools import partial
from botocore.exceptions import ClientError
from typing import Optional, Dict
from app.config import settings

# Cognito 클라이언트 생성
cognito_client = boto3.client(
    'cognito-idp',
    region_name=settings.AWS_REGION
)


class CognitoService:
    """Cognito 인증 서비스"""

    @staticmethod
    async def sign_up(email: str, password: str, name: str) -> Dict:
        """
        Cognito에 사용자 등록
        
        Args:
            email: 이메일 주소
            password: 비밀번호
            name: 사용자 이름
            
        Returns:
            사용자 정보 딕셔너리 (sub 포함)
            
        Raises:
            ClientError: Cognito API 오류
        """
        loop = asyncio.get_event_loop()
        try:
            response = await loop.run_in_executor(
                None,
                partial(
                    cognito_client.sign_up,
                    ClientId=settings.COGNITO_CLIENT_ID,
                    Username=email,
                    Password=password,
                    UserAttributes=[
                        {'Name': 'email', 'Value': email},
                        {'Name': 'name', 'Value': name},
                    ],
                )
            )
            return response
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == 'UsernameExistsException':
                raise ValueError('이미 사용 중인 이메일입니다')
            elif error_code == 'InvalidPasswordException':
                raise ValueError('비밀번호가 요구사항을 만족하지 않습니다')
            elif error_code == 'InvalidParameterException':
                raise ValueError('입력값이 올바르지 않습니다')
            raise ValueError(f'회원가입 실패: {e.response.get("Error", {}).get("Message", str(e))}')

    @staticmethod
    async def admin_initiate_auth(email: str, password: str) -> Dict:
        """
        Cognito 관리자 인증 (로그인)
        
        Args:
            email: 이메일 주소
            password: 비밀번호
            
        Returns:
            인증 토큰 딕셔너리 (AccessToken, IdToken, RefreshToken 포함)
            
        Raises:
            ClientError: Cognito API 오류
        """
        loop = asyncio.get_event_loop()
        try:
            # Secret이 있는 경우 SECRET_HASH 추가
            auth_parameters = {
                'USERNAME': email,
                'PASSWORD': password,
            }
            
            if settings.COGNITO_CLIENT_SECRET:
                import hmac
                import hashlib
                import base64
                
                message = email + settings.COGNITO_CLIENT_ID
                dig = hmac.new(
                    settings.COGNITO_CLIENT_SECRET.encode('utf-8'),
                    message.encode('utf-8'),
                    hashlib.sha256
                ).digest()
                secret_hash = base64.b64encode(dig).decode()
                auth_parameters['SECRET_HASH'] = secret_hash

            response = await loop.run_in_executor(
                None,
                partial(
                    cognito_client.admin_initiate_auth,
                    UserPoolId=settings.COGNITO_USER_POOL_ID,
                    ClientId=settings.COGNITO_CLIENT_ID,
                    AuthFlow='ADMIN_NO_SRP_AUTH',
                    AuthParameters=auth_parameters,
                )
            )
            return response.get('AuthenticationResult', {})
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == 'NotAuthorizedException':
                raise ValueError('이메일 또는 비밀번호가 올바르지 않습니다')
            elif error_code == 'UserNotFoundException':
                raise ValueError('사용자를 찾을 수 없습니다')
            elif error_code == 'UserNotConfirmedException':
                raise ValueError('이메일 인증이 완료되지 않았습니다')
            raise ValueError(f'로그인 실패: {e.response.get("Error", {}).get("Message", str(e))}')

    @staticmethod
    async def confirm_sign_up(email: str, code: str) -> Dict:
        """
        이메일 인증번호 확인 및 계정 활성화

        Args:
            email: 이메일 주소
            code: 인증번호 (6자리)

        Returns:
            확인 결과
        """
        loop = asyncio.get_event_loop()
        try:
            # Secret Hash 생성 (필요한 경우)
            params = {
                'ClientId': settings.COGNITO_CLIENT_ID,
                'Username': email,
                'ConfirmationCode': code,
            }

            if settings.COGNITO_CLIENT_SECRET:
                import hmac
                import hashlib
                import base64

                message = email + settings.COGNITO_CLIENT_ID
                dig = hmac.new(
                    settings.COGNITO_CLIENT_SECRET.encode('utf-8'),
                    message.encode('utf-8'),
                    hashlib.sha256
                ).digest()
                secret_hash = base64.b64encode(dig).decode()
                params['SecretHash'] = secret_hash

            response = await loop.run_in_executor(
                None,
                partial(cognito_client.confirm_sign_up, **params)
            )
            return response
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == 'CodeMismatchException':
                raise ValueError('인증번호가 올바르지 않습니다')
            elif error_code == 'ExpiredCodeException':
                raise ValueError('인증번호가 만료되었습니다. 재발송해주세요')
            elif error_code == 'NotAuthorizedException':
                raise ValueError('이미 인증된 계정입니다')
            raise ValueError(f'인증 실패: {e.response.get("Error", {}).get("Message", str(e))}')

    @staticmethod
    async def resend_confirmation_code(email: str) -> Dict:
        """
        인증번호 재발송

        Args:
            email: 이메일 주소

        Returns:
            발송 결과
        """
        loop = asyncio.get_event_loop()
        try:
            params = {
                'ClientId': settings.COGNITO_CLIENT_ID,
                'Username': email,
            }

            if settings.COGNITO_CLIENT_SECRET:
                import hmac
                import hashlib
                import base64

                message = email + settings.COGNITO_CLIENT_ID
                dig = hmac.new(
                    settings.COGNITO_CLIENT_SECRET.encode('utf-8'),
                    message.encode('utf-8'),
                    hashlib.sha256
                ).digest()
                secret_hash = base64.b64encode(dig).decode()
                params['SecretHash'] = secret_hash

            response = await loop.run_in_executor(
                None,
                partial(cognito_client.resend_confirmation_code, **params)
            )
            return response
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == 'UserNotFoundException':
                raise ValueError('등록되지 않은 이메일입니다')
            elif error_code == 'InvalidParameterException':
                raise ValueError('이미 인증된 계정입니다')
            raise ValueError(f'재발송 실패: {e.response.get("Error", {}).get("Message", str(e))}')

    @staticmethod
    async def admin_get_user(email: str) -> Dict:
        """
        관리자 권한으로 사용자 정보 조회

        Args:
            email: 이메일 주소

        Returns:
            사용자 정보 딕셔너리
        """
        loop = asyncio.get_event_loop()
        try:
            response = await loop.run_in_executor(
                None,
                partial(
                    cognito_client.admin_get_user,
                    UserPoolId=settings.COGNITO_USER_POOL_ID,
                    Username=email
                )
            )
            return response
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == 'UserNotFoundException':
                raise ValueError('사용자를 찾을 수 없습니다')
            raise ValueError(f'사용자 조회 실패: {e.response.get("Error", {}).get("Message", str(e))}')

    @staticmethod
    async def get_user(access_token: str) -> Dict:
        """
        Cognito에서 사용자 정보 조회
        
        Args:
            access_token: Cognito Access Token
            
        Returns:
            사용자 정보 딕셔너리
        """
        loop = asyncio.get_event_loop()
        try:
            response = await loop.run_in_executor(
                None,
                partial(cognito_client.get_user, AccessToken=access_token)
            )
            return response
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == 'NotAuthorizedException':
                raise ValueError('유효하지 않은 토큰입니다')
            raise ValueError(f'사용자 정보 조회 실패: {e.response.get("Error", {}).get("Message", str(e))}')

    @staticmethod
    async def get_user_by_sub(sub: str) -> Optional[Dict]:
        """
        Cognito Sub로 사용자 조회
        
        Args:
            sub: Cognito User Sub (UUID)
            
        Returns:
            사용자 정보 딕셔너리 또는 None
        """
        loop = asyncio.get_event_loop()
        try:
            response = await loop.run_in_executor(
                None,
                partial(
                    cognito_client.admin_get_user,
                    UserPoolId=settings.COGNITO_USER_POOL_ID,
                    Username=sub
                )
            )
            return response
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == 'UserNotFoundException':
                return None
            raise ValueError(f'사용자 조회 실패: {e.response.get("Error", {}).get("Message", str(e))}')

    @staticmethod
    def parse_user_attributes(user_attributes: list) -> Dict[str, str]:
        """
        Cognito UserAttributes를 딕셔너리로 변환
        
        Args:
            user_attributes: Cognito UserAttributes 리스트
            
        Returns:
            속성 딕셔너리
        """
        result = {}
        for attr in user_attributes:
            result[attr['Name']] = attr['Value']
        return result

    @staticmethod
    async def verify_id_token(id_token: str) -> Dict:
        """
        Cognito ID Token 검증 및 디코딩
        
        Args:
            id_token: Cognito ID Token
            
        Returns:
            디코딩된 토큰 페이로드
            
        Raises:
            ValueError: 토큰 검증 실패
        """
        import jwt
        import requests
        from jose import jwk, jwt as jose_jwt
        from jose.utils import base64url_decode
        
        try:
            # JWKS URL 구성
            jwks_url = f"https://cognito-idp.{settings.AWS_REGION}.amazonaws.com/{settings.COGNITO_USER_POOL_ID}/.well-known/jwks.json"
            
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"JWKS URL: {jwks_url}")
            
            # JWKS 가져오기
            loop = asyncio.get_event_loop()
            jwks_response = await loop.run_in_executor(
                None,
                requests.get,
                jwks_url
            )
            
            if jwks_response.status_code != 200:
                logger.error(f"JWKS 조회 실패: status={jwks_response.status_code}, body={jwks_response.text}")
                raise ValueError(f"JWKS 조회 실패: {jwks_response.status_code}")
                
            jwks = jwks_response.json()
            
            # 토큰 헤더에서 kid 추출
            headers = jwt.get_unverified_header(id_token)
            kid = headers.get('kid')
            logger.info(f"Token KID: {kid}")
            
            # kid에 해당하는 키 찾기
            key = None
            for jwk_key in jwks.get('keys', []):
                if jwk_key.get('kid') == kid:
                    key = jwk_key
                    break
            
            if not key:
                raise ValueError('토큰 검증 키를 찾을 수 없습니다')
            
            # 토큰 검증 및 디코딩
            public_key = jwk.construct(key)
            message, encoded_signature = str(id_token).rsplit('.', 1)
            decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
            
            if not public_key.verify(message.encode("utf-8"), decoded_signature):
                raise ValueError('토큰 서명이 유효하지 않습니다')
            
            # 토큰 디코딩
            claims = jose_jwt.get_unverified_claims(id_token)
            
            # 토큰 만료 확인
            import time
            if claims.get('exp', 0) < time.time():
                raise ValueError('토큰이 만료되었습니다')
            
            # 토큰 발급자 확인
            expected_issuer = f"https://cognito-idp.{settings.AWS_REGION}.amazonaws.com/{settings.COGNITO_USER_POOL_ID}"
            if claims.get('iss') != expected_issuer:
                raise ValueError('토큰 발급자가 올바르지 않습니다')
            
            # 클라이언트 ID 확인
            token_use = claims.get('token_use')
            if token_use != 'id':
                raise ValueError('ID Token이 아닙니다')
            
            return claims
        except Exception as e:
            raise ValueError(f'토큰 검증 실패: {str(e)}')

    @staticmethod
    async def exchange_code_for_token(code: str) -> str:
        """
        Authorization Code를 ID Token으로 교환
        
        Args:
            code: Cognito Authorization Code
            
        Returns:
            ID Token
            
        Raises:
            ValueError: 토큰 교환 실패
        """
        import requests
        
        try:
            # 토큰 교환 URL
            token_url = f"{settings.COGNITO_DOMAIN}/oauth2/token"
            
            # 요청 파라미터
            data = {
                'grant_type': 'authorization_code',
                'client_id': settings.COGNITO_CLIENT_ID,
                'code': code,
                'redirect_uri': settings.COGNITO_REDIRECT_URI,
            }
            
            # Client Secret이 있는 경우 추가
            if settings.COGNITO_CLIENT_SECRET:
                data['client_secret'] = settings.COGNITO_CLIENT_SECRET
            
            # 토큰 교환
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(token_url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
            )
            
            if response.status_code != 200:
                raise ValueError(f'토큰 교환 실패: {response.text}')
            
            token_data = response.json()
            id_token = token_data.get('id_token')
            
            if not id_token:
                raise ValueError('ID Token을 받을 수 없습니다')
            
            return id_token
        except Exception as e:
            raise ValueError(f'토큰 교환 실패: {str(e)}')

