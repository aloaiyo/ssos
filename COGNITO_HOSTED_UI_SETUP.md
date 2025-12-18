# Cognito Hosted UI 활성화 및 도메인 설정 가이드

## 1. AWS Cognito 콘솔 접속

1. [AWS Console](https://console.aws.amazon.com/)에 로그인
2. 검색창에 "Cognito" 입력
3. **Amazon Cognito** 선택

---

## 2. User Pool 생성 (아직 없는 경우)

### 2.1 User Pool 생성 시작
1. 왼쪽 메뉴에서 **사용자 풀** 클릭
2. **사용자 풀 만들기** 버튼 클릭

### 2.2 로그인 옵션 설정
- **로그인 옵션**:
  - ✅ **이메일** 선택
  - Google은 나중에 추가 가능

### 2.3 비밀번호 정책 설정
- 원하는 정책 선택 (기본값 사용 가능)

### 2.4 MFA 설정
- **MFA 필수 아님** 선택 (개발 환경)
- 또는 원하는 설정 선택

### 2.5 사용자 풀 속성 설정
- ✅ **이메일** 선택
- ✅ **이름** 선택 (given_name, family_name)
- 필요시 다른 속성 추가

### 2.6 사용자 풀 만들기
1. **사용자 풀 만들기** 버튼 클릭
2. 생성 완료 후 **사용자 풀 ID** 복사 (나중에 필요)

---

## 3. App Client 생성 및 Hosted UI 활성화

### 3.1 App Client 생성
1. 생성한 User Pool 클릭
2. 왼쪽 메뉴에서 **앱 통합** 클릭
3. **앱 클라이언트** 섹션으로 스크롤
4. **앱 클라이언트 만들기** 버튼 클릭

### 3.2 App Client 설정
1. **앱 클라이언트 이름** 입력: `ssos-frontend` (원하는 이름)

2. **클라이언트 보안 비밀번호 생성**:
   - ✅ 체크: Secret이 있는 경우 (더 안전)
   - ❌ 체크 해제: Secret이 없는 경우 (간단)

3. **인증 흐름 구성**:
   - ✅ **ALLOW_USER_PASSWORD_AUTH** 체크
   - ✅ **ALLOW_REFRESH_TOKEN_AUTH** 체크
   - ✅ **ALLOW_USER_SRP_AUTH** 체크

4. **OAuth 2.0 설정** 섹션:
   - ✅ **Cognito Hosted UI 활성화** 체크 (중요!)
   
5. **콜백 URL** 입력:
   ```
   http://localhost:3000/auth/callback
   ```
   - **+ URL 추가** 버튼으로 여러 개 추가 가능
   - 프로덕션 URL도 나중에 추가 가능

6. **로그아웃 URL** 입력:
   ```
   http://localhost:3000
   ```
   - **+ URL 추가** 버튼으로 여러 개 추가 가능

7. **허용된 OAuth 흐름**:
   - ✅ **Authorization code grant** 체크 (필수)
   - ❌ **Implicit grant** (선택 사항, 보안상 권장하지 않음)

8. **허용된 OAuth 범위**:
   - ✅ **openid** 체크
   - ✅ **email** 체크
   - ✅ **profile** 체크

9. **앱 클라이언트 만들기** 버튼 클릭

### 3.3 App Client 정보 복사
생성 후 다음 정보를 복사해두세요:
- **앱 클라이언트 ID**
- **앱 클라이언트 보안 비밀번호** (Secret이 있는 경우)

---

## 4. Hosted UI 도메인 설정

### 4.1 도메인 섹션으로 이동
1. User Pool 선택
2. 왼쪽 메뉴에서 **앱 통합** 클릭
3. **도메인** 섹션으로 스크롤

### 4.2 Cognito 도메인 선택
1. **Cognito 도메인** 라디오 버튼 선택
2. **도메인 접두사** 입력:
   - 예: `ssos-tennis-club`
   - ⚠️ 고유한 이름이어야 함 (다른 사용자가 사용 중이면 안됨)
   - 영문 소문자, 숫자, 하이픈(-)만 사용 가능
   - 최소 4자, 최대 63자

3. **사용 가능 여부 확인** 버튼 클릭
   - ✅ 사용 가능: 초록색 체크 표시
   - ❌ 사용 불가: 빨간색 X 표시 → 다른 이름 시도

4. 사용 가능하면 **도메인 저장** 버튼 클릭

### 4.3 도메인 정보 확인
저장 후 다음 정보가 표시됩니다:
- **도메인 이름**: `ssos-tennis-club.auth.ap-northeast-2.amazoncognito.com`
- 이 값을 복사해두세요 (Backend/Frontend 설정에 필요)

### 4.4 사용자 지정 도메인 (선택 사항)
프로덕션 환경에서는 사용자 지정 도메인을 사용할 수 있습니다:
1. **사용자 지정 도메인** 라디오 버튼 선택
2. Route 53에서 도메인 인증서 설정 필요
3. 개발 환경에서는 Cognito 도메인 사용 권장

---

## 5. App Client 설정 확인 및 수정

### 5.1 App Client 설정 확인
1. **앱 통합** > **앱 클라이언트** 섹션
2. 생성한 App Client 클릭
3. **호스트된 UI 편집** 버튼 클릭

### 5.2 ID 공급자 설정
**ID 공급자** 섹션에서:
- ✅ **Cognito 사용자 풀** 체크 (이메일/비밀번호 로그인)
- ✅ **Google** 체크 (Google 소셜 로그인, 나중에 추가)

### 5.3 콜백 URL 확인
**콜백 URL** 섹션에서:
- `http://localhost:3000/auth/callback` 확인

### 5.4 로그아웃 URL 확인
**로그아웃 URL** 섹션에서:
- `http://localhost:3000` 확인

### 5.5 저장
**저장 변경 사항** 버튼 클릭

---

## 6. Hosted UI 테스트

### 6.1 Hosted UI URL 확인
1. **앱 통합** > **도메인** 섹션
2. **호스트된 UI 시작** 버튼 클릭
3. 브라우저에서 Hosted UI 페이지가 열림

### 6.2 로그인 테스트
1. Hosted UI에서 이메일/비밀번호로 로그인 시도
2. 또는 Google 버튼 클릭 (Google 설정 후)

---

## 7. 설정 확인 체크리스트

설정이 완료되었는지 확인:

- [ ] User Pool 생성 완료
- [ ] App Client 생성 완료
- [ ] **Cognito Hosted UI 활성화** 체크됨
- [ ] 콜백 URL 설정: `http://localhost:3000/auth/callback`
- [ ] 로그아웃 URL 설정: `http://localhost:3000`
- [ ] Authorization code grant 활성화
- [ ] openid, email, profile 범위 활성화
- [ ] Cognito 도메인 생성 완료
- [ ] 도메인 이름 복사 완료
- [ ] App Client ID 복사 완료
- [ ] App Client Secret 복사 완료 (있는 경우)

---

## 8. 주요 설정 위치 요약

### App Client 생성 및 Hosted UI 활성화
**경로**: User Pool > 앱 통합 > 앱 클라이언트 > 앱 클라이언트 만들기
- ✅ **Cognito Hosted UI 활성화** 체크
- 콜백 URL 입력
- 로그아웃 URL 입력
- OAuth 흐름 및 범위 설정

### 도메인 설정
**경로**: User Pool > 앱 통합 > 도메인
- Cognito 도메인 선택
- 도메인 접두사 입력
- 사용 가능 여부 확인
- 도메인 저장

### ID 공급자 설정
**경로**: User Pool > 앱 통합 > 앱 클라이언트 > 호스트된 UI 편집
- Cognito 사용자 풀 체크
- Google 체크 (나중에)

---

## 9. 문제 해결

### 문제: "Cognito Hosted UI 활성화" 옵션이 보이지 않음
- **원인**: App Client 생성 중 OAuth 2.0 설정을 건너뛰었을 수 있음
- **해결**: App Client를 삭제하고 다시 생성하거나, 기존 App Client의 "호스트된 UI 편집"에서 활성화

### 문제: "도메인을 사용할 수 없음"
- **원인**: 다른 사용자가 이미 사용 중이거나 형식이 잘못됨
- **해결**: 
  - 다른 이름 시도 (예: `ssos-tennis-club-2024`)
  - 영문 소문자, 숫자, 하이픈만 사용
  - 최소 4자 이상

### 문제: "콜백 URL이 작동하지 않음"
- **원인**: URL 형식이 잘못되었거나 허용되지 않은 문자 포함
- **해결**: 
  - `http://localhost:3000/auth/callback` 형식 확인
  - 슬래시(/)로 끝나지 않도록 주의
  - 프로토콜(`http://` 또는 `https://`) 포함 확인

### 문제: Hosted UI가 열리지 않음
- **원인**: 도메인이 제대로 저장되지 않았을 수 있음
- **해결**: 
  - 도메인 섹션에서 도메인 상태 확인
  - 필요시 도메인 삭제 후 재생성

---

## 10. 다음 단계

Hosted UI 활성화 및 도메인 설정이 완료되면:

1. ✅ Backend `.env` 파일에 설정 추가
2. ✅ Frontend `.env` 파일에 설정 추가
3. ✅ Google Identity Provider 추가 (선택 사항)
4. ✅ 로그인 테스트

자세한 내용은 `COGNITO_GOOGLE_SETUP.md` 파일 참조

---

**설정 중 문제가 있으면 알려주세요!**


