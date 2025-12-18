# Cognito Google 소셜 로그인 설정 가이드

## 1. Google Cloud Console 설정

### 1.1 Google Cloud 프로젝트 생성
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택

### 1.2 OAuth 2.0 클라이언트 ID 생성
1. **API 및 서비스** > **사용자 인증 정보** 메뉴로 이동
2. **+ 사용자 인증 정보 만들기** > **OAuth 클라이언트 ID** 선택
3. **애플리케이션 유형**: 웹 애플리케이션
4. **이름**: `SSOS Tennis Club` (원하는 이름)
5. **승인된 리디렉션 URI** 추가:
   ```
   https://your-cognito-domain.auth.ap-northeast-2.amazoncognito.com/oauth2/idpresponse
   ```
   ⚠️ **중요**: `your-cognito-domain`은 실제 Cognito 도메인으로 변경 필요
6. **만들기** 클릭
7. **클라이언트 ID**와 **클라이언트 보안 비밀번호** 복사 (나중에 필요)

### 1.3 OAuth 동의 화면 설정
1. **OAuth 동의 화면** 메뉴로 이동
2. **외부** 선택 (내부는 Google Workspace 전용)
3. 필수 정보 입력:
   - 앱 이름: `SSOS Tennis Club`
   - 사용자 지원 이메일: 본인 이메일
   - 개발자 연락처 정보: 본인 이메일
4. **저장 후 계속** 클릭
5. **범위** 단계에서 기본 범위 유지 (이메일, 프로필, 열기)
6. **저장 후 계속** 클릭
7. **테스트 사용자** 추가 (테스트 중인 경우)
8. 완료

---

## 2. AWS Cognito 설정

### 2.1 Cognito User Pool 생성 (아직 없는 경우)
1. [AWS Cognito Console](https://console.aws.amazon.com/cognito/) 접속
2. **사용자 풀 만들기** 클릭
3. **로그인 옵션**:
   - ✅ 이메일
   - ✅ Google (나중에 추가)
4. **비밀번호 정책**: 원하는 정책 설정
5. **MFA**: 선택 사항
6. **사용자 풀 속성**:
   - ✅ 이메일
   - ✅ 이름 (given_name, family_name)
7. **사용자 풀 만들기** 클릭

### 2.2 App Client 생성
1. **앱 통합** 탭으로 이동
2. **앱 클라이언트** 섹션에서 **앱 클라이언트 만들기** 클릭
3. 설정:
   - **앱 클라이언트 이름**: `ssos-frontend`
   - **클라이언트 보안 비밀번호 생성**: 선택 (Secret이 있는 경우)
   - **인증 흐름**:
     - ✅ ALLOW_USER_PASSWORD_AUTH
     - ✅ ALLOW_REFRESH_TOKEN_AUTH
     - ✅ ALLOW_USER_SRP_AUTH
   - **OAuth 2.0 설정**:
     - ✅ Cognito Hosted UI 활성화
     - **콜백 URL**: 
       ```
       http://localhost:3000/auth/callback
       ```
     - **로그아웃 URL**:
       ```
       http://localhost:3000
       ```
     - **허용된 OAuth 흐름**:
       - ✅ Authorization code grant
       - ✅ Implicit grant (선택 사항)
     - **허용된 OAuth 범위**:
       - ✅ openid
       - ✅ email
       - ✅ profile
4. **앱 클라이언트 만들기** 클릭
5. **앱 클라이언트 ID**와 **앱 클라이언트 보안 비밀번호** 복사

### 2.3 Hosted UI 도메인 설정
1. **앱 통합** 탭 > **도메인** 섹션
2. **Cognito 도메인** 선택 (또는 사용자 지정 도메인)
3. 도메인 이름 입력 (예: `ssos-tennis-club`)
4. **사용 가능 여부 확인** 클릭
5. 사용 가능하면 **도메인 저장** 클릭
6. **도메인 이름** 복사 (예: `ssos-tennis-club.auth.ap-northeast-2.amazoncognito.com`)

### 2.4 Google Identity Provider 추가
1. **앱 통합** 탭 > **연동** 섹션
2. **소셜 ID 공급자** 섹션에서 **Google** 클릭
3. 설정:
   - **Google 클라이언트 ID**: Google Cloud Console에서 복사한 클라이언트 ID
   - **Google 클라이언트 보안 비밀번호**: Google Cloud Console에서 복사한 클라이언트 보안 비밀번호
   - **허용된 범위**: `openid email profile`
4. **저장** 클릭

### 2.5 Identity Provider를 App Client에 연결
1. **앱 통합** 탭 > **앱 클라이언트 설정** 섹션
2. 생성한 앱 클라이언트 선택
3. **호스트된 UI 편집** 클릭
4. **ID 공급자** 섹션에서:
   - ✅ Cognito 사용자 풀 (이메일/비밀번호 로그인)
   - ✅ Google (방금 추가한 것)
5. **저장 변경 사항** 클릭

---

## 3. Backend 환경 변수 설정

`backend/.env` 파일에 다음 정보를 추가/수정:

```env
# AWS Cognito 설정
AWS_REGION=ap-northeast-2
COGNITO_USER_POOL_ID=ap-northeast-2_XXXXXXXXX  # Cognito User Pool ID
COGNITO_CLIENT_ID=XXXXXXXXXXXXXXXXXXXXXXXXXX    # App Client ID
COGNITO_CLIENT_SECRET=XXXXXXXXXXXXXXXXXXXXXXXX  # App Client Secret (있는 경우)
COGNITO_DOMAIN=ssos-tennis-club.auth.ap-northeast-2.amazoncognito.com  # Hosted UI 도메인
COGNITO_REDIRECT_URI=http://localhost:3000/auth/callback
COGNITO_SIGN_OUT_URI=http://localhost:3000
```

### 각 값 찾는 방법:
- **COGNITO_USER_POOL_ID**: 
  - Cognito Console > 사용자 풀 선택 > 일반 설정 > 사용자 풀 ID
- **COGNITO_CLIENT_ID**: 
  - Cognito Console > 앱 통합 > 앱 클라이언트 > 앱 클라이언트 ID
- **COGNITO_CLIENT_SECRET**: 
  - Cognito Console > 앱 통합 > 앱 클라이언트 > 앱 클라이언트 보안 비밀번호
  - ⚠️ Secret이 없는 경우 빈 값으로 두거나 주석 처리
- **COGNITO_DOMAIN**: 
  - Cognito Console > 앱 통합 > 도메인 > 도메인 이름

---

## 4. Frontend 환경 변수 설정

`frontend/.env` 파일 생성/수정:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_COGNITO_DOMAIN=https://ssos-tennis-club.auth.ap-northeast-2.amazoncognito.com
VITE_COGNITO_CLIENT_ID=XXXXXXXXXXXXXXXXXXXXXXXXXX
VITE_COGNITO_REDIRECT_URI=http://localhost:3000/auth/callback
VITE_COGNITO_SIGN_OUT_URI=http://localhost:3000
```

### 각 값 찾는 방법:
- **VITE_COGNITO_DOMAIN**: 
  - Backend의 `COGNITO_DOMAIN`과 동일하지만 `https://` 접두사 추가
- **VITE_COGNITO_CLIENT_ID**: 
  - Backend의 `COGNITO_CLIENT_ID`와 동일

---

## 5. Google Cloud Console 리디렉션 URI 확인

Google Cloud Console에서 설정한 리디렉션 URI가 다음 형식인지 확인:

```
https://[YOUR_COGNITO_DOMAIN]/oauth2/idpresponse
```

예시:
```
https://ssos-tennis-club.auth.ap-northeast-2.amazoncognito.com/oauth2/idpresponse
```

⚠️ **중요**: 
- `http://localhost:3000/auth/callback`이 **아닙니다**
- Cognito 도메인을 사용해야 합니다
- Google이 Cognito로 리디렉션하고, Cognito가 다시 우리 앱으로 리디렉션합니다

---

## 6. 테스트

### 6.1 서버 실행
```bash
# Backend
cd backend
poetry run uvicorn app.main:app --reload

# Frontend (새 터미널)
cd frontend
npm run dev
```

### 6.2 로그인 테스트
1. 브라우저에서 `http://localhost:3000` 접속
2. 로그인 페이지에서 "로그인하기" 버튼 클릭
3. Cognito Hosted UI가 열림
4. **Google** 버튼 클릭
5. Google 계정 선택 및 로그인
6. 권한 승인
7. 자동으로 앱으로 리디렉션되어 로그인 완료

---

## 7. 문제 해결

### 문제: "리디렉션 URI 불일치" 오류
- **원인**: Google Cloud Console의 리디렉션 URI가 잘못됨
- **해결**: `https://[COGNITO_DOMAIN]/oauth2/idpresponse` 형식인지 확인

### 문제: "Cognito에서 Google을 찾을 수 없음"
- **원인**: Identity Provider가 App Client에 연결되지 않음
- **해결**: 앱 클라이언트 설정에서 Google을 허용된 ID 공급자로 선택

### 문제: "토큰 교환 실패"
- **원인**: Backend의 `COGNITO_REDIRECT_URI`가 Frontend와 일치하지 않음
- **해결**: 두 파일의 리디렉션 URI가 정확히 일치하는지 확인

### 문제: "도메인을 사용할 수 없음"
- **원인**: 도메인 이름이 이미 사용 중이거나 형식이 잘못됨
- **해결**: 다른 도메인 이름 시도 또는 사용자 지정 도메인 사용

---

## 8. 프로덕션 배포 시 추가 설정

프로덕션 환경에서는 다음 URL도 추가해야 합니다:

### Google Cloud Console
- 승인된 리디렉션 URI에 프로덕션 URL 추가:
  ```
  https://your-production-domain.com/auth/callback
  ```

### Cognito App Client
- 콜백 URL에 프로덕션 URL 추가:
  ```
  https://your-production-domain.com/auth/callback
  ```
- 로그아웃 URL에 프로덕션 URL 추가:
  ```
  https://your-production-domain.com
  ```

### 환경 변수
- Backend와 Frontend의 환경 변수도 프로덕션 URL로 업데이트

---

## 체크리스트

설정 완료 후 확인:

- [ ] Google Cloud Console에서 OAuth 클라이언트 ID 생성 완료
- [ ] Google Cloud Console에 Cognito 리디렉션 URI 추가 완료
- [ ] Cognito User Pool 생성 완료
- [ ] Cognito App Client 생성 완료
- [ ] Cognito Hosted UI 도메인 설정 완료
- [ ] Cognito에 Google Identity Provider 추가 완료
- [ ] App Client에 Google ID 공급자 연결 완료
- [ ] Backend `.env` 파일 설정 완료
- [ ] Frontend `.env` 파일 설정 완료
- [ ] 로그인 테스트 성공

---

**설정이 완료되면 위 체크리스트를 확인하고, 문제가 있으면 알려주세요!**


