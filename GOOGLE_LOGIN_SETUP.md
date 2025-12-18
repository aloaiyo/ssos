# Google Social Login Setup Guide

이 가이드는 AWS Cognito User Pool에 Google 소셜 로그인을 연동하는 방법을 설명합니다.

## 1. Google Cloud Platform (GCP) 설정

### 1.1 프로젝트 생성
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 (예: `tennis-club-auth`)

### 1.2 OAuth 동의 화면 구성
1. **API 및 서비스** > **OAuth 동의 화면** 이동
2. **User Type**: **외부 (External)** 선택 후 만들기
3. **앱 정보** 입력:
   - 앱 이름: `Tennis Club`
   - 사용자 지원 이메일: 본인 이메일
4. **개발자 연락처 정보**: 본인 이메일
5. **저장 후 계속** 클릭 (범위 설정 등은 기본값 유지)

### 1.3 OAuth 클라이언트 ID 생성
1. **API 및 서비스** > **사용자 인증 정보** 이동
2. **+ 사용자 인증 정보 만들기** > **OAuth 클라이언트 ID** 선택
3. **애플리케이션 유형**: **웹 애플리케이션**
4. **이름**: `Cognito Client`
5. **승인된 리디렉션 URI** 추가:
   - 형식: `https://<your-cognito-domain>/oauth2/idpresponse`
   - 예: `https://ssos-tennis-club.auth.ap-northeast-2.amazoncognito.com/oauth2/idpresponse`
   - **주의**: Cognito 도메인 주소여야 합니다. (localhost 아님)
6. **만들기** 클릭
7. **클라이언트 ID**와 **클라이언트 보안 비밀(Secret)** 복사

---

## 2. AWS Cognito 설정

### 2.1 Google ID 공급자 추가
1. [AWS Cognito Console](https://console.aws.amazon.com/cognito) > **사용자 풀** 선택
2. **로그인 경험** 탭 클릭
3. **연동 자격 증명 공급자 로그인** 섹션에서 **ID 공급자 추가** 클릭
4. **Google** 선택
5. 정보 입력:
   - **클라이언트 ID**: GCP에서 복사한 값
   - **클라이언트 보안 비밀**: GCP에서 복사한 값
   - **승인된 범위**: `profile email openid`
6. **속성 매핑**:
   - `email` -> `email`
   - `given_name` -> `given_name` (또는 `name`)
   - `family_name` -> `family_name`
   - `picture` -> `picture` (선택 사항)
7. **ID 공급자 추가** 클릭

### 2.2 앱 클라이언트 설정 업데이트
1. **앱 통합** 탭 클릭
2. **앱 클라이언트 목록**에서 `ssos-frontend` 클릭
3. **호스트된 UI** 섹션의 **편집** 클릭
4. **ID 공급자** 목록에서 **Google** 체크
5. **변경 사항 저장** 클릭

---

## 3. 테스트

1. 프론트엔드 앱 실행 (`npm run dev`)
2. 로그인 페이지 접속
3. **로그인하기** 버튼 클릭 -> Cognito Hosted UI로 이동
4. **Continue with Google** 버튼 확인 및 클릭
5. Google 로그인 진행
6. 앱으로 리다이렉트 및 로그인 성공 확인
