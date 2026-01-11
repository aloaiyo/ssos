# SSOS - 테니스 동호회 관리 시스템

## 📋 프로젝트 개요

테니스 동호회 관리를 위한 웹 서비스. 핵심 기능은 공정한 경기 스케줄링을 위한 **자동 매치 생성** 알고리즘.

| 구분 | 기술 스택 |
|------|----------|
| Backend | FastAPI + Tortoise-ORM + PostgreSQL |
| Frontend | Vue 3 + Vuetify 3 + Pinia |
| Auth | AWS Cognito (Google SSO 지원) |
| Infra | AWS EC2 + RDS + SSM Parameter Store |

---

## 🏗️ 아키텍처

### 인증 흐름 (AWS Cognito + HTTP-only Cookie)

```
┌─────────────┐     ┌─────────────────────┐     ┌─────────────┐
│  Frontend   │────▶│ Cognito Hosted UI   │────▶│  Backend    │
│  (Vue 3)    │     │ (Google/Email)      │     │  (FastAPI)  │
└─────────────┘     └─────────────────────┘     └─────────────┘
       │                     │                         │
       │ 1. Login Button     │ 2. Auth Code           │
       │────────────────────▶│────────────────────────▶│
       │                     │                         │
       │                     │ 3. Exchange for Token   │
       │                     │                         │
       │ 4. HTTP-only Cookie (Local JWT)              │
       │◀─────────────────────────────────────────────│
       │                                               │
       │ 5. API Calls with Cookie                     │
       │─────────────────────────────────────────────▶│
```

### 멀티테넌트 데이터 모델

```
User (전역 사용자, cognito_sub 연결)
  └── ClubMember (동호회 회원, role: manager/member)
        └── Club (동호회) ← 테넌트 격리 경계
              ├── Season (시즌) ← 랭킹 집계 기간
              │     ├── SeasonRanking (시즌별 랭킹)
              │     └── Session (세션, via Event)
              ├── Event (일정)
              │     └── Session (세션)
              │           ├── SessionParticipant (참가자)
              │           └── Match (경기)
              │                 ├── MatchParticipant (경기 참가자)
              │                 └── MatchResult (경기 결과)
              ├── Guest (게스트 참가자)
              ├── Ranking (전체 랭킹)
              ├── ClubSchedule (정기 일정)
              ├── Announcement (공지)
              └── Fee (회비)
```

> ⚠️ **중요**: 모든 동호회 관련 쿼리는 반드시 `club_id`로 필터링하여 테넌트 격리 유지

---

## 📁 디렉토리 구조

### Backend (`backend/app/`)

```
app/
├── main.py                    # FastAPI 앱 엔트리포인트
├── config.py                  # 설정 관리 (AWS SSM 지원)
│
├── models/                    # Tortoise-ORM 모델
│   ├── __init__.py           # 모델 export
│   ├── base.py               # BaseModel (soft delete, timestamps)
│   ├── user.py               # User, UserFavoriteClub
│   ├── club.py               # Club
│   ├── member.py             # ClubMember
│   ├── event.py              # Event, Session, SessionConfig, SessionParticipant
│   ├── match.py              # Match, MatchParticipant, MatchResult
│   ├── ranking.py            # Ranking
│   ├── season.py             # Season, SeasonRanking
│   ├── schedule.py           # ClubSchedule
│   ├── announcement.py       # Announcement
│   ├── fee.py                # Fee
│   └── guest.py              # Guest (비회원 참가자)
│
├── schemas/                   # Pydantic V2 스키마
│   ├── user.py               # 사용자 관련 요청/응답
│   ├── club.py               # 동호회 관련
│   ├── member.py             # 회원 관련
│   ├── event.py              # 일정/세션 관련
│   ├── match.py              # 경기 관련
│   ├── ranking.py            # 랭킹 관련
│   ├── season.py             # 시즌 관련
│   └── schedule.py           # 정기 일정 관련
│
├── api/                       # FastAPI 라우터
│   ├── auth.py               # 인증 (쿠키 기반 JWT)
│   ├── users.py              # 사용자 관리
│   ├── clubs.py              # 동호회 CRUD
│   ├── members.py            # 회원 관리
│   ├── events.py             # 일정 관리
│   ├── sessions.py           # 세션 관리
│   ├── matches.py            # 경기 관리 + 자동 생성
│   ├── rankings.py           # 랭킹 조회
│   ├── seasons.py            # 시즌 관리
│   ├── announcements.py      # 공지 관리
│   ├── fees.py               # 회비 관리
│   └── guests.py             # 게스트 관리
│
├── services/                  # 비즈니스 로직
│   ├── auth_service.py       # 인증 서비스
│   ├── cognito_service.py    # AWS Cognito API 래퍼
│   └── matching_service.py   # 매치 생성 알고리즘 ⭐
│
└── core/                      # 핵심 유틸리티
    ├── security.py           # JWT 토큰 생성/검증
    └── dependencies.py       # FastAPI 의존성 주입
```

### Frontend (`frontend/src/`)

```
src/
├── main.js                    # Vue 앱 엔트리포인트
├── App.vue                    # 루트 컴포넌트
│
├── router/
│   └── index.js              # Vue Router + 인증 가드
│
├── stores/                    # Pinia 상태 관리
│   ├── auth.js               # 인증 상태
│   ├── club.js               # 동호회 상태
│   ├── member.js             # 회원 상태
│   ├── season.js             # 시즌 상태
│   ├── session.js            # 세션 상태
│   ├── match.js              # 경기 상태
│   └── ranking.js            # 랭킹 상태
│
├── api/                       # Axios API 클라이언트
│   ├── index.js              # Axios 인스턴스 + 인터셉터
│   ├── auth.js               # 인증 API
│   ├── clubs.js              # 동호회 API
│   ├── members.js            # 회원 API
│   ├── events.js             # 일정 API
│   ├── sessions.js           # 세션 API
│   ├── matches.js            # 경기 API
│   ├── rankings.js           # 랭킹 API
│   ├── seasons.js            # 시즌 API
│   ├── guests.js             # 게스트 API
│   └── token.js              # 토큰 유틸리티
│
├── views/                     # 페이지 컴포넌트
│   ├── LandingView.vue       # 랜딩 페이지
│   ├── HomeView.vue          # 대시보드
│   ├── NotFoundView.vue      # 404 페이지
│   │
│   ├── auth/                 # 인증 페이지
│   │   ├── LoginView.vue     # 로그인
│   │   ├── RegisterView.vue  # 회원가입
│   │   ├── CallbackView.vue  # OAuth 콜백
│   │   ├── VerifyEmailView.vue        # 이메일 인증
│   │   └── ProfileCompletionView.vue  # 프로필 완성
│   │
│   ├── club/                 # 동호회 페이지
│   │   ├── ClubListView.vue  # 동호회 목록
│   │   ├── ClubDetailView.vue # 동호회 상세
│   │   ├── ClubCreateView.vue # 동호회 생성
│   │   ├── ClubManageView.vue # 동호회 관리
│   │   └── components/       # 동호회 탭 컴포넌트
│   │       ├── ClubInfoTab.vue
│   │       ├── ClubStatsTab.vue
│   │       ├── MemberManagementTab.vue
│   │       ├── SessionManagementTab.vue
│   │       ├── AnnouncementTab.vue
│   │       └── FeeManagementTab.vue
│   │
│   ├── member/               # 회원 페이지
│   │   ├── MemberListView.vue
│   │   └── MemberManageView.vue
│   │
│   ├── season/               # 시즌 페이지
│   │   ├── SeasonListView.vue
│   │   └── SeasonDetailView.vue
│   │
│   ├── session/              # 세션 페이지
│   │   ├── SessionListView.vue
│   │   ├── SessionCreateView.vue
│   │   └── SessionDetailView.vue
│   │
│   ├── match/                # 경기 페이지
│   │   ├── MatchScheduleView.vue
│   │   ├── MatchGenerateView.vue
│   │   └── MatchResultView.vue
│   │
│   └── ranking/              # 랭킹 페이지
│       └── RankingView.vue
│
├── components/                # 재사용 컴포넌트
│   ├── layout/
│   │   ├── AppBar.vue        # 상단 네비게이션
│   │   ├── NavigationDrawer.vue # 사이드바
│   │   └── Footer.vue
│   │
│   ├── common/
│   │   ├── LoadingSpinner.vue
│   │   ├── ErrorAlert.vue
│   │   └── WeeklySchedulePicker.vue
│   │
│   └── match/
│       ├── MatchCard.vue     # 경기 카드
│       └── MatchSchedule.vue # 경기 스케줄
│
├── plugins/
│   └── vuetify.js            # Vuetify 설정
│
├── styles/
│   └── main.css              # 전역 스타일
│
└── utils/
    ├── date.js               # 날짜 유틸리티
    └── validators.js         # 유효성 검증
```

---

## 🎯 핵심 알고리즘: 매치 생성

**파일**: `backend/app/services/matching_service.py`

세션 참가자로부터 공정한 경기 스케줄 생성:

```python
async def create_matches_for_session(
    session_id: int,
    participants: List[SessionParticipant],
    num_courts: int,
    match_duration_minutes: int,
    start_time: time
) -> List[Match]:
```

### 매치 타입별 처리

| 타입 | 코드 | 설명 | 필요 인원 |
|------|------|------|----------|
| 남자 복식 | `MENS_DOUBLES` | 남자 4명 (2v2) | 4+ |
| 혼합 복식 | `MIXED_DOUBLES` | 남녀 각 2명 (1m+1f vs 1m+1f) | 남2+여2 |
| 단식 | `SINGLES` | 1v1 | 2+ |

### 알고리즘 흐름

1. **타입별 분류**: 참가자를 `participation_type`으로 그룹화
2. **랜덤 셔플**: 공정성을 위한 무작위 배열
3. **성별 페어링**: 혼복은 남녀 균형 맞춤
4. **코트 배정**: 라운드 로빈 방식
5. **시간 스케줄링**: `match_duration_minutes` 기반

---

## 📊 데이터 모델 상세

### User (전역 사용자)

```python
class User(BaseModel):
    email: str              # 이메일 (unique)
    cognito_sub: str        # Cognito 사용자 ID (unique)
    name: str               # 이름
    role: UserRole          # user | super_admin
    subscription_tier: SubscriptionTier  # free | premium
    gender: str             # male | female (nullable)
    birth_date: date        # 생년월일 (nullable)
```

### Club (동호회)

```python
class Club(BaseModel):
    name: str
    description: str
    created_by: FK(User)
    location: str                  # 활동 장소
    default_num_courts: int        # 기본 코트 수
    default_match_duration: int    # 기본 경기 시간 (분)
    default_day_of_week: int       # 정기 활동 요일 (0=월)
    default_start_time: time
    default_end_time: time
```

### ClubMember (동호회 회원)

```python
class ClubMember(BaseModel):
    club: FK(Club)
    user: FK(User)
    role: MemberRole        # manager | member | guest
    status: MemberStatus    # pending | active | inactive | left | banned
    gender: Gender          # male | female
    nickname: str           # 클럽 내 닉네임
    total_games: int
    wins: int
    losses: int
    draws: int
```

**회원 역할**:
| 역할 | 설명 | 권한 |
|------|------|------|
| manager | 동호회 관리자 | 모든 권한, 회원/게스트 관리 |
| member | 일반 회원 | 일정, 경기, 회원 목록 조회 |
| guest | 게스트 (가입 사용자) | 일정, 본인 경기만 조회 (회원 목록 조회 불가) |

**회원 상태**:
| 상태 | 설명 |
|------|------|
| pending | 가입 대기 (승인 필요) |
| active | 활성 (승인됨) |
| inactive | 비활성 |
| left | 탈퇴 |
| banned | 추방됨 |

### Guest (미가입 게스트)

```python
class Guest(BaseModel):
    club: FK(Club)
    name: str
    gender: Gender
    phone: str              # 연락처 (선택)
    notes: str              # 메모
    # 연결 정보
    linked_member: FK(ClubMember)  # 연결된 회원 (가입 시)
    created_by: FK(ClubMember)     # 생성한 매니저
    # 통계
    total_games: int
    wins: int
    losses: int
    draws: int
```

**게스트 유형**:
| 유형 | 설명 | User 연결 |
|------|------|----------|
| 미가입 게스트 (Guest 모델) | 매니저가 생성한 미가입 참가자 | 없음 |
| 가입 게스트 (ClubMember role=guest) | 서비스 가입 후 게스트로 참여 | 있음 |

**게스트-회원 연결 흐름**:
1. 매니저가 미가입 게스트(Guest) 생성
2. 해당 참가자가 서비스 가입 → ClubMember 생성
3. 매니저가 Guest와 ClubMember 연결 (경기 기록 이전)

### Season (시즌)

```python
class Season(BaseModel):
    club: FK(Club)
    name: str               # "2024 상반기", "Winter League"
    description: str
    start_date: date
    end_date: date
    status: SeasonStatus    # upcoming | active | completed
```

### SeasonRanking (시즌별 랭킹)

```python
class SeasonRanking(BaseModel):
    season: FK(Season)
    club_member: FK(ClubMember)
    total_matches: int
    wins: int
    draws: int
    losses: int
    points: int             # 승3점/무1점/패0점
    rank: int               # 순위
```

### Session (세션)

```python
class Session(BaseModel):
    event: FK(Event)
    season: FK(Season)      # 시즌 연결 (nullable)
    date: date
    start_time: time
    end_time: time
    num_courts: int
    match_duration_minutes: int
    session_type: SessionType    # league | tournament
    status: SessionStatus        # draft | confirmed | completed
```

### Match (경기)

```python
class Match(BaseModel):
    session: FK(Session)
    match_number: int
    court_number: int
    scheduled_time: time
    match_type: MatchType    # mens_doubles | mixed_doubles | singles
    status: MatchStatus      # scheduled | in_progress | completed
```

### SessionParticipant / MatchParticipant (참가자)

```python
# 참가자 유형에 따라 하나만 설정
club_member: FK(ClubMember)  # 정회원
guest: FK(Guest)             # 게스트 (시스템 미가입)
user: FK(User)               # 준회원 (시스템 가입, 동호회 미가입)

participant_category: ParticipantCategory  # member | guest | associate
```

---

## 🔐 API 엔드포인트

### 인증 (`/api/auth`)

| Method | Path | 설명 |
|--------|------|------|
| POST | `/register` | 회원가입 (이메일 인증번호 발송) |
| POST | `/verify-email` | 이메일 인증 + 자동 로그인 |
| POST | `/resend-code` | 인증번호 재발송 |
| POST | `/login` | 이메일/비밀번호 로그인 |
| POST | `/logout` | 로그아웃 (쿠키 삭제) |
| POST | `/callback` | OAuth 콜백 (구글 로그인) |
| POST | `/refresh` | 토큰 갱신 |
| GET | `/me` | 현재 사용자 정보 |
| PUT | `/me` | 프로필 수정 |
| GET | `/check` | 인증 상태 확인 |

### 동호회 (`/api/clubs`)

| Method | Path | 설명 |
|--------|------|------|
| GET | `/` | 동호회 목록 |
| POST | `/` | 동호회 생성 |
| GET | `/{id}` | 동호회 상세 |
| PUT | `/{id}` | 동호회 수정 |
| DELETE | `/{id}` | 동호회 삭제 |
| POST | `/{id}/join` | 동호회 가입 신청 |

### 회원 (`/api/clubs/{club_id}/members`)

| Method | Path | 설명 | 권한 |
|--------|------|------|------|
| GET | `/` | 회원 목록 조회 | 매니저/일반회원 (게스트 제외) |
| POST | `/{member_id}/approve` | 회원 승인 | 매니저 |
| PUT | `/{member_id}` | 역할 변경 (manager/member/guest) | 매니저 |
| DELETE | `/{member_id}` | 회원 내보내기 | 매니저 |

### 게스트 (`/api/clubs/{club_id}/guests`)

| Method | Path | 설명 | 권한 |
|--------|------|------|------|
| GET | `/` | 게스트 목록 | 매니저/일반회원 (게스트 제외) |
| POST | `/` | 게스트 생성 | 매니저 |
| GET | `/{guest_id}` | 게스트 상세 | 매니저/일반회원 |
| PUT | `/{guest_id}` | 게스트 수정 | 매니저 |
| POST | `/{guest_id}/link` | 게스트-회원 연결 | 매니저 |
| DELETE | `/{guest_id}/link` | 연결 해제 | 매니저 |
| DELETE | `/{guest_id}` | 게스트 삭제 | 매니저 |

### 시즌 (`/api/seasons`)

| Method | Path | 설명 |
|--------|------|------|
| GET | `/` | 시즌 목록 (club_id 필터) |
| POST | `/` | 시즌 생성 |
| GET | `/{id}` | 시즌 상세 |
| PUT | `/{id}` | 시즌 수정 |
| DELETE | `/{id}` | 시즌 삭제 |
| GET | `/{id}/rankings` | 시즌 랭킹 조회 |
| GET | `/{id}/sessions` | 시즌 세션 목록 |

### 경기 (`/api/sessions/{session_id}/matches`)

| Method | Path | 설명 |
|--------|------|------|
| GET | `/` | 세션의 경기 목록 |
| POST | `/generate` | **자동 매치 생성** ⭐ |
| PUT | `/{match_id}/result` | 경기 결과 입력 |

---

## ⚙️ 환경 설정

### Backend (`.env`)

```env
DATABASE_URL=postgres://postgres:password@localhost:5432/tennis_club
SECRET_KEY=your-secret-key
USE_AWS_SSM=False

# AWS Cognito
COGNITO_USER_POOL_ID=ap-northeast-2_xxxxx
COGNITO_CLIENT_ID=xxxxxxxxx
COGNITO_CLIENT_SECRET=xxxxxxxxx
COGNITO_DOMAIN=https://your-domain.auth.ap-northeast-2.amazoncognito.com
COGNITO_REDIRECT_URI=http://localhost:3000/auth/callback
COGNITO_SIGN_OUT_URI=http://localhost:3000

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Frontend (`.env`)

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_COGNITO_DOMAIN=https://your-domain.auth.ap-northeast-2.amazoncognito.com
VITE_COGNITO_CLIENT_ID=xxxxxxxxx
VITE_COGNITO_REDIRECT_URI=http://localhost:3000/auth/callback
VITE_COGNITO_SIGN_OUT_URI=http://localhost:3000
```

---

## 🚀 빠른 시작

```bash
# Backend
cd backend
poetry install
createdb tennis_club
poetry run aerich init -t app.config.TORTOISE_ORM
poetry run aerich init-db
poetry run uvicorn app.main:app --reload  # http://localhost:8000

# Frontend (별도 터미널)
cd frontend
npm install
npm run dev  # http://localhost:3000

# 또는 동시 실행
./start_dev.sh
```

---

## ⚠️ 주의사항

| 영역 | 주의점 |
|------|--------|
| Aerich | 모델 변경 후 `migrate` → `upgrade` 순서 |
| Aerich Migration Naming | 파일명은 4자리 숫자 prefix 사용: `0000_`, `0001_`, `0002_`, `0003_` (예: `0003_20260111_add_feature.py`) |
| Tortoise | 모든 DB 작업에 `await` 필수 (`.count()`, `.exists()` 포함) |
| Pydantic V2 | `model_config = ConfigDict(from_attributes=True)` 사용 |
| Cognito | 백엔드가 로컬 JWT 발급; 프론트는 로컬 토큰만 사용 |
| CORS | Backend 8000, Frontend 3000/5173 |
| 테넌트 격리 | 동호회 쿼리 시 항상 `club_id` 필터 필수 |

---

## 📚 관련 문서

- [CLAUDE.md](./CLAUDE.md) - Claude Code 가이드
- [PROJECT_OVERVIEW.md](./PROJECT_OVERVIEW.md) - 프로젝트 상세 개요
- [QUICKSTART.md](./QUICKSTART.md) - 빠른 시작 가이드
- [README.md](./README.md) - 프로젝트 소개
- [COGNITO_HOSTED_UI_SETUP.md](./COGNITO_HOSTED_UI_SETUP.md) - Cognito 설정
- [COGNITO_GOOGLE_SETUP.md](./COGNITO_GOOGLE_SETUP.md) - 구글 SSO 설정
