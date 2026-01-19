# API Reference

## 개요

모든 API는 `/api` prefix를 사용하며, HTTP-only 쿠키 기반 인증을 사용합니다.

**Base URL**: `http://localhost:8000/api`

---

## 인증 (Auth)

### 회원가입
```
POST /api/auth/register
```
**Body:**
```json
{
  "email": "user@example.com",
  "password": "Password123!",
  "name": "홍길동"
}
```
**Response:** Cognito 인증번호 이메일 발송

### 이메일 인증
```
POST /api/auth/verify-email
```
**Body:**
```json
{
  "email": "user@example.com",
  "code": "123456"
}
```
**Response:** 자동 로그인 + 쿠키 설정

### OAuth 콜백
```
POST /api/auth/callback
```
**Body:**
```json
{
  "code": "authorization_code_from_cognito"
}
```
**Response:** 사용자 정보 + 쿠키 설정

### 토큰 갱신
```
POST /api/auth/refresh-token
```
**Response:** 새 토큰 쿠키 설정

### 로그아웃
```
POST /api/auth/logout
```
**Response:** 쿠키 삭제

### 현재 사용자
```
GET /api/auth/me
PUT /api/auth/me
```

---

## 동호회 (Clubs)

### 동호회 목록
```
GET /api/clubs?search=테니스&page=1&limit=20
```

### 동호회 CRUD
```
POST   /api/clubs
GET    /api/clubs/{club_id}
PUT    /api/clubs/{club_id}
DELETE /api/clubs/{club_id}
```

### 정기 스케줄
```
GET    /api/clubs/{club_id}/schedules
POST   /api/clubs/{club_id}/schedules
PUT    /api/clubs/{club_id}/schedules    # 일괄 업데이트
```

---

## 회원 (Members)

### 회원 목록
```
GET /api/clubs/{club_id}/members?status=active
```
**Query Params:**
- `status`: pending, active, inactive, left, banned

### 회원 관리 (매니저 전용)
```
POST   /api/clubs/{club_id}/members           # 가입 신청
POST   /api/clubs/{club_id}/members/{id}/approve
POST   /api/clubs/{club_id}/members/{id}/reject
PATCH  /api/clubs/{club_id}/members/{id}/role
DELETE /api/clubs/{club_id}/members/{id}
```

---

## 게스트 (Guests)

```
GET    /api/clubs/{club_id}/guests
POST   /api/clubs/{club_id}/guests
PATCH  /api/clubs/{club_id}/guests/{id}
DELETE /api/clubs/{club_id}/guests/{id}
POST   /api/clubs/{club_id}/guests/{id}/link   # 회원과 연결
```

---

## 시즌 (Seasons)

### 시즌 목록
```
GET /api/clubs/{club_id}/seasons?status=active
```
**Query Params:**
- `status`: upcoming, active, completed

### 시즌 CRUD
```
POST   /api/clubs/{club_id}/seasons
GET    /api/clubs/{club_id}/seasons/{id}
PUT    /api/clubs/{club_id}/seasons/{id}
DELETE /api/clubs/{club_id}/seasons/{id}
```

### 시즌 랭킹
```
GET /api/clubs/{club_id}/seasons/{id}/rankings
```

---

## 세션 (Sessions)

### 세션 목록
```
GET /api/clubs/{club_id}/sessions?season_id=1
```

### 세션 CRUD
```
POST   /api/clubs/{club_id}/sessions
GET    /api/clubs/{club_id}/sessions/{id}
PUT    /api/clubs/{club_id}/sessions/{id}
DELETE /api/clubs/{club_id}/sessions/{id}
```

### 참가자 관리
```
GET    /api/clubs/{club_id}/sessions/{id}/participants
POST   /api/clubs/{club_id}/sessions/{id}/participants
DELETE /api/clubs/{club_id}/sessions/{id}/participants/{pid}
```

### 자동 매칭 생성
```
POST /api/clubs/{club_id}/sessions/{id}/matches/generate
POST /api/clubs/{club_id}/sessions/{id}/matches/generate-ai    # AI 매칭 미리보기
POST /api/clubs/{club_id}/sessions/{id}/matches/confirm-ai     # AI 매칭 확정
```
**Description:** 참가자들로부터 경기 자동 생성
- 남복: 4명씩 2v2
- 여복: 4명씩 2v2
- 혼복: 남녀 페어링 (각 팀 남1, 여1)
- 단식: 2명씩 1v1

---

## 경기 (Matches)

### 경기 목록
```
GET /api/matches?session_id=1
```

### 경기 CRUD
```
POST   /api/matches
GET    /api/matches/{id}
PUT    /api/matches/{id}
DELETE /api/matches/{id}
```

### 경기 참가자
```
GET  /api/matches/{id}/participants
POST /api/matches/{id}/participants
```

### 경기 결과
```
GET  /api/matches/{id}/result
POST /api/matches/{id}/result
PUT  /api/matches/{id}/result
```

**Body (결과 등록):**
```json
{
  "team_a_score": 6,
  "team_b_score": 4,
  "winner_team": "A"
}
```

---

## 랭킹 (Rankings)

### 전체 랭킹 (시즌 독립)
```
GET /api/rankings?club_id=1
GET /api/rankings/{id}
```

---

## 공지사항 (Announcements)

```
GET    /api/clubs/{club_id}/announcements
POST   /api/clubs/{club_id}/announcements          # 매니저 전용
GET    /api/clubs/{club_id}/announcements/{id}
PUT    /api/clubs/{club_id}/announcements/{id}     # 매니저 전용
DELETE /api/clubs/{club_id}/announcements/{id}     # 매니저 전용
```

---

## 회비 (Fees)

### 회비 정책
```
GET  /api/clubs/{club_id}/fees
POST /api/clubs/{club_id}/fees        # 매니저 전용
PUT  /api/clubs/{club_id}/fees/{id}   # 매니저 전용
```

### 납부 기록
```
GET  /api/clubs/{club_id}/fee-payments
POST /api/clubs/{club_id}/fee-payments        # 매니저 전용
PUT  /api/clubs/{club_id}/fee-payments/{id}
```

---

## 일정 (Events)

```
GET    /api/events?club_id=1
POST   /api/events
GET    /api/events/{id}
PUT    /api/events/{id}
DELETE /api/events/{id}
```

---

## 사용자 (Users)

```
GET /api/users/me/clubs    # 현재 사용자의 가입 동호회 목록
```

---

## 권한 체계

| 역할 | 권한 |
|------|------|
| **MANAGER** | 회원 승인/거절/제거, 역할 변경, 세션/경기 생성, 결과 등록, 공지 작성, 회비 설정 |
| **MEMBER** | 조회 전체, 납부 현황 조회 |
| **GUEST** | 세션/경기 조회 (회원 목록 제외) |

---

## 에러 응답

```json
{
  "detail": "에러 메시지"
}
```

| 코드 | 의미 |
|------|------|
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Internal Server Error |

---

## OCR (스코어 이미지 처리)

```
POST /api/ocr/extract        # 이미지에서 스코어 추출
POST /api/ocr/save-matches   # OCR 결과로 경기 저장
```

---

## API 문서

백엔드 실행 시: http://localhost:8000/docs (Swagger UI)

---

*Last Updated: 2026-01-19*
