"""
애플리케이션 설정 관리
"""
import os
import boto3
from botocore.exceptions import ClientError
from pydantic_settings import BaseSettings
from typing import List, Optional


def get_ssm_parameter(name: str, with_decryption: bool = True) -> Optional[str]:
    """AWS SSM Parameter Store에서 파라미터 조회"""
    try:
        ssm = boto3.client("ssm", region_name=os.getenv("AWS_REGION", "ap-northeast-2"))
        response = ssm.get_parameter(Name=name, WithDecryption=with_decryption)
        return response["Parameter"]["Value"]
    except ClientError as e:
        print(f"SSM 파라미터 조회 실패 ({name}): {e}")
        return None
    except Exception as e:
        print(f"SSM 연결 오류: {e}")
        return None


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # AWS SSM 설정
    USE_AWS_SSM: bool = False
    AWS_REGION: str = "ap-northeast-2"
    
    # SSM 파라미터 경로 접두사
    SSM_PREFIX: str = "/tennis-club/prod"

    # 데이터베이스
    DATABASE_URL: str = "postgres://postgres:password@localhost:5432/tennis_club"

    # JWT 설정
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 30       # 액세스 토큰 30일
    REFRESH_TOKEN_EXPIRE_DAYS: int = 365     # 리프레시 토큰 365일

    # 쿠키 설정
    COOKIE_SECURE: bool = False  # 개발: False, 프로덕션: True (HTTPS)
    COOKIE_SAMESITE: str = "lax"

    # 애플리케이션
    APP_NAME: str = "Tennis Club Management System"
    DEBUG: bool = True

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # AWS Cognito 설정
    COGNITO_USER_POOL_ID: str = ""
    COGNITO_CLIENT_ID: str = ""
    COGNITO_CLIENT_SECRET: str = ""
    
    # Cognito Hosted UI 설정
    COGNITO_DOMAIN: str = ""  # 예: your-domain.auth.ap-northeast-2.amazoncognito.com
    COGNITO_REDIRECT_URI: str = "http://localhost:3000/auth/callback"
    COGNITO_SIGN_OUT_URI: str = "http://localhost:3000"

    def model_post_init(self, __context):
        """설정 초기화 후 SSM에서 값 로드"""
        if self.USE_AWS_SSM:
            print("AWS SSM Parameter Store에서 설정을 로드합니다...")
            
            # 데이터베이스 URL
            db_url = get_ssm_parameter(f"{self.SSM_PREFIX}/database_url")
            if db_url:
                self.DATABASE_URL = db_url
                
            # Secret Key
            secret_key = get_ssm_parameter(f"{self.SSM_PREFIX}/secret_key")
            if secret_key:
                self.SECRET_KEY = secret_key
                
            # Cognito Client Secret
            client_secret = get_ssm_parameter(f"{self.SSM_PREFIX}/cognito_client_secret")
            if client_secret:
                self.COGNITO_CLIENT_SECRET = client_secret
                
            print("SSM 설정 로드 완료")

    @property
    def cors_origins_list(self) -> List[str]:
        """CORS origin 목록 반환"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # .env 파일의 추가 필드 무시


settings = Settings()

# Tortoise ORM 설정
TORTOISE_ORM = {
    "connections": {
        "default": settings.DATABASE_URL
    },
    "apps": {
        "models": {
            "models": [
                "app.models.user",
                "app.models.club",
                "app.models.member",
                "app.models.event",
                "app.models.match",
                "app.models.ranking",
                "app.models.announcement",
                "app.models.fee",
                "app.models.schedule",
                "app.models.guest",
                "aerich.models"
            ],
            "default_connection": "default",
        },
    },
}
