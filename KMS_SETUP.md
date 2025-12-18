# AWS KMS & SSM Parameter Store Setup Guide

이 가이드는 백엔드 애플리케이션의 민감한 설정(DB 접속 정보, 비밀 키 등)을 AWS Systems Manager (SSM) Parameter Store와 KMS를 사용하여 안전하게 관리하는 방법을 설명합니다.

## 1. AWS KMS (Key Management Service) 설정

1. [AWS KMS Console](https://console.aws.amazon.com/kms) 접속
2. **고객 관리형 키** > **키 만들기** 클릭
3. **키 유형**: 대칭(Symmetric)
4. **키 사용**: 암호화 및 복호화
5. **별칭**: `alias/tennis-club-key` (원하는 이름)
6. **키 관리자** 및 **키 사용자**: 본인 IAM 사용자 선택
7. **완료** 클릭

## 2. SSM Parameter Store 설정

[AWS Systems Manager Console](https://console.aws.amazon.com/systems-manager/parameters) > **Parameter Store** 접속

다음 파라미터들을 생성합니다. (유형: **SecureString**, KMS 키: 위에서 생성한 키 선택)

| 이름 | 설명 | 예시 값 |
|------|------|---------|
| `/tennis-club/prod/database_url` | DB 접속 URL | `postgres://user:pass@host:5432/db` |
| `/tennis-club/prod/secret_key` | JWT 서명 키 | `random-secret-string` |
| `/tennis-club/prod/cognito_client_secret` | Cognito Client Secret | `your-client-secret` (있는 경우) |

### 파라미터 생성 방법 (콘솔)
1. **파라미터 생성** 클릭
2. **이름**: `/tennis-club/prod/database_url`
3. **유형**: **SecureString**
4. **KMS 키 소스**: **내 현재 계정** -> 위에서 생성한 키 선택
5. **값**: 실제 데이터베이스 URL 입력
6. **파라미터 생성** 클릭
7. 나머지 파라미터도 동일하게 반복

## 3. 로컬 개발 환경 설정

로컬에서 AWS SSM에 접근하려면 AWS 자격 증명이 필요합니다.

### 3.1 AWS CLI 설치 및 설정
```bash
aws configure
# AWS Access Key ID 입력
# AWS Secret Access Key 입력
# Default region name: ap-northeast-2
# Default output format: json
```

### 3.2 백엔드 환경 변수 설정 (.env)
```ini
# .env 파일
USE_AWS_SSM=true
AWS_REGION=ap-northeast-2
```

## 4. 권한 설정 (EC2 배포 시)

EC2 인스턴스에서 실행할 경우, EC2 IAM Role에 다음 정책이 필요합니다:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ssm:GetParameters",
                "ssm:GetParameter"
            ],
            "Resource": "arn:aws:ssm:ap-northeast-2:YOUR_ACCOUNT_ID:parameter/tennis-club/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "kms:Decrypt"
            ],
            "Resource": "arn:aws:kms:ap-northeast-2:YOUR_ACCOUNT_ID:key/YOUR_KEY_ID"
        }
    ]
}
```
