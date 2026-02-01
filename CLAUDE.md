# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 언어 설정 (Language)

**항상 한글로 응답하세요.** Always respond in Korean.

## Project Overview

**테니스 동호회 관리 시스템** - Tennis club management web service with FastAPI backend and Vue 3 frontend. Core feature: automated match generation for fair game scheduling.

**Tech Stack**: FastAPI + Tortoise-ORM + PostgreSQL | Vue 3 + Vuetify 3 + Pinia | AWS Cognito

## Quick Start

### Backend
```bash
cd backend
poetry install
createdb tennis_club
poetry run aerich init -t app.config.TORTOISE_ORM
poetry run aerich init-db
poetry run uvicorn app.main:app --reload  # http://localhost:8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev  # http://localhost:3000
```

### Both at once
```bash
./start_dev.sh
```

## Key Commands

### Backend
```bash
# Database migrations
poetry run aerich migrate --name "description"
poetry run aerich upgrade
poetry run aerich downgrade

# Formatting
poetry run black .
poetry run isort .

# Tests
poetry run pytest
poetry run pytest --cov=app
poetry run pytest tests/test_matching_service.py  # Single file
```

### Frontend
```bash
npm run dev      # Dev server
npm run build    # Production build
npm run preview  # Preview production build
npm run lint     # ESLint 검사
npm run lint:fix # ESLint 자동 수정
```

## Architecture

### Authentication Flow (AWS Cognito + HTTP-only Cookies)

The system uses **AWS Cognito** for authentication with **HTTP-only cookies** for security:

1. **Cognito Hosted UI** handles login/signup (Google SSO supported)
2. Backend exchanges Cognito tokens for **local JWT tokens**
3. Backend sets JWT as **HTTP-only cookie** (not localStorage)
4. All subsequent API calls use cookies automatically

```
Frontend → Cognito Hosted UI → Authorization Code
    ↓
Backend /api/auth/callback → Exchange code for Cognito ID Token
    ↓
Verify ID Token → Sync/Create local User → Set HTTP-only cookie
    ↓
Frontend API calls include cookie automatically
```

**Key files**:
- `backend/app/services/cognito_service.py` - Cognito API wrapper
- `backend/app/services/auth_service.py` - Token exchange, user sync
- `backend/app/core/dependencies.py` - Cookie-based authentication dependencies
- `frontend/src/api/auth.js` - Cognito redirect URLs, API calls
- `frontend/src/views/auth/CallbackView.vue` - OAuth callback handler

### Multi-Tenant Data Model

```
User (전역 사용자, cognito_sub linked)
  └── ClubMember (동호회 회원, role: manager/member)
        └── Club (동호회) ← tenant isolation boundary
              ├── Season (시즌) ← ranking aggregation period
              │     ├── Session (세션, linked via Event)
              │     └── SeasonRanking (시즌별 랭킹)
              ├── Event (일정)
              │     └── Session (세션)
              │           ├── SessionParticipant
              │           └── Match (경기)
              │                 └── MatchParticipant
              │                       └── MatchResult
              ├── Guest (게스트 참가자)
              ├── Announcement (공지사항)
              └── Fee (회비)
```

**Important**: All club-related queries MUST filter by `club_id` for tenant isolation.

### Backend Structure

```
backend/app/
├── models/       # Tortoise-ORM models
│   ├── user.py, club.py, member.py     # Core entities
│   ├── season.py                        # Season & SeasonRanking
│   ├── event.py, match.py, ranking.py   # Game management
│   └── guest.py, fee.py, announcement.py # Auxiliary features
├── schemas/      # Pydantic V2 schemas
├── api/          # FastAPI routes (sessions.py가 가장 복잡, 매칭 생성 포함)
├── services/     # Business logic
│   ├── auth_service.py, cognito_service.py  # 인증
│   ├── matching_service.py                   # 기본 매칭 알고리즘
│   ├── ai_matching_service.py                # AI 기반 매칭
│   └── ocr_service.py                        # 결과 이미지 OCR
├── core/         # security.py (JWT), dependencies.py (DI with cookie auth)
└── config.py     # Settings with AWS SSM support
```

### Frontend Structure

```
frontend/src/
├── views/        # Page components (auth/, club/, member/, session/, season/, match/, ranking/, profile/)
├── components/   # Reusable (layout/, common/, match/)
├── stores/       # Pinia stores (auth, club, member, session, season, match, ranking)
├── api/          # Axios clients (withCredentials: true for cookies)
├── router/       # Vue Router with auth guards + profile completion check
├── utils/        # date.js (날짜 포맷), sanitize 등
└── plugins/      # Vuetify config
```

**Router Guard Flow**:
1. 인증 체크 → 미인증 시 로그인 페이지
2. 프로필 완성 체크 → 미완성 시 프로필 완성 페이지로 리다이렉트
3. 관리자 권한 체크 (특정 페이지)

## Core Algorithm: Match Generation

**Location**: `backend/app/services/matching_service.py` (기본), `ai_matching_service.py` (AI 기반)

Generates fair game schedules from session participants:
1. Group by match type (mens_doubles, mixed_doubles, singles)
2. Gender pairing for mixed doubles
3. Random shuffle for fairness
4. Court allocation and time scheduling

**Match Types**:
- `MENS_DOUBLES` (남복): 4 male (2v2)
- `WOMENS_DOUBLES` (여복): 4 female (2v2)
- `MIXED_DOUBLES` (혼복): 2 male + 2 female (1m+1f vs 1m+1f)
- `SINGLES` (단식): 2 players (1v1)

**Additional Services**:
- `ocr_service.py` - 경기 결과 이미지 OCR 처리 (Google Gemini API)

## Development Patterns

### Timezone Handling (UTC Storage, KST Display)

**백엔드**: 모든 datetime은 UTC로 저장, KST로 응답
```python
from app.core.timezone import KST, to_utc, to_kst

# 저장 시: KST → UTC
start_kst = datetime.combine(date, start_time, tzinfo=KST)
start_datetime_utc = to_utc(start_kst)
await Session.create(start_datetime=start_datetime_utc, ...)

# 조회 시: UTC → KST
return {"date": to_kst(session.start_datetime).isoformat()}
```

**프론트엔드**: JavaScript Date의 `toISOString()`은 UTC로 변환되므로 주의!
```javascript
// ❌ 잘못된 방법 - UTC로 변환되어 날짜가 하루 밀릴 수 있음
date.toISOString().split('T')[0]

// ✅ 올바른 방법 - 로컬 날짜 사용
const year = date.getFullYear()
const month = String(date.getMonth() + 1).padStart(2, '0')
const day = String(date.getDate()).padStart(2, '0')
return `${year}-${month}-${day}`
```

**Session 모델**: `start_datetime`/`end_datetime` (UTC) 필드 사용, `date`/`start_time`/`end_time`은 KST 프로퍼티

### Pydantic V2 (Backend)
```python
from pydantic import BaseModel, ConfigDict

class ClubSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # NOT Config.orm_mode
    id: int
    name: str
```

### Tortoise-ORM Async
```python
# Always await, including count/exists
club = await Club.get(id=club_id).prefetch_related('members__user')
members = await ClubMember.filter(club_id=club_id)
count = await Match.filter(session_id=session_id).count()

# Transactions
from tortoise.transactions import in_transaction
async with in_transaction():
    match = await Match.create(...)
    await MatchParticipant.create(match=match, ...)
```

### Vue 3 Composition API
```vue
<script setup>
import { ref, onMounted } from 'vue'
import { useClubStore } from '@/stores/club'

const clubStore = useClubStore()
onMounted(async () => {
  await clubStore.fetchClubs()  // Use store actions, not direct API calls
})
</script>
```

### API Clients (Cookie-based)
`frontend/src/api/index.js` handles:
- `withCredentials: true` for automatic cookie inclusion
- Axios interceptors for error handling
- CORS requires explicit credentials support

### Permission Dependencies
```python
from app.core.dependencies import (
    get_current_user,           # Basic auth via cookie
    get_current_active_user,    # Active user check
    require_super_admin,        # Super admin only
    require_club_member,        # Club membership check
    require_club_manager,       # Club manager role check
)
```

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgres://postgres:password@localhost:5432/tennis_club
SECRET_KEY=your-secret-key
COGNITO_USER_POOL_ID=ap-northeast-2_xxxxx
COGNITO_CLIENT_ID=xxxxxxxxxxxxxxxxx
COGNITO_CLIENT_SECRET=xxxxxxxxxxxxxxxxx
COGNITO_DOMAIN=https://your-domain.auth.ap-northeast-2.amazoncognito.com
COGNITO_REDIRECT_URI=http://localhost:3000/auth/callback
USE_AWS_SSM=False  # Set True in production to load secrets from SSM
```

### Frontend (.env)
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_COGNITO_DOMAIN=https://your-domain.auth.ap-northeast-2.amazoncognito.com
VITE_COGNITO_CLIENT_ID=xxxxxxxxxxxxxxxxx
VITE_COGNITO_REDIRECT_URI=http://localhost:3000/auth/callback
VITE_COGNITO_SIGN_OUT_URI=http://localhost:3000
```

## Security Patterns

### XSS Prevention
사용자 입력 콘텐츠를 `v-html`로 렌더링할 때는 반드시 DOMPurify로 sanitize:
```javascript
import DOMPurify from 'dompurify'

function formatContent(content) {
  const sanitized = DOMPurify.sanitize(content, { ALLOWED_TAGS: [] })
  return sanitized.replace(/\n/g, '<br>')
}
```

### Production Build
- `console.log`는 프로덕션 빌드에서 자동 제거 (vite.config.js의 esbuild.drop 설정)
- ESLint에서 `no-console` 규칙으로 개발 중 경고

## Common Gotchas

- **Aerich**: Run `migrate` before `upgrade` after model changes
- **Aerich Migration Naming**: 파일명은 반드시 **4자리 숫자 prefix** 사용
  - 형식: `NNNN_YYYYMMDDHHMMSS_description.py` (예: `0005_20260131194857_datetime_timezone_refactor.py`)
  - ❌ 잘못된 예: `5_20260131_...` (prefix가 4자리가 아님)
  - ✅ 올바른 예: `0005_20260131_...` (4자리 prefix)
  - Aerich가 자동 생성 시 prefix가 누락될 수 있으니 생성 후 확인 필요
- **Tortoise**: ALL db operations need `await`, even `.count()`, `.exists()`
- **Pydantic V2**: Use `model_config = ConfigDict(from_attributes=True)`
- **Cookies**: Frontend must use `withCredentials: true` for Axios; Backend CORS must allow credentials
- **CORS**: Backend 8000, Frontend 3000 - configured in `config.py` with `allow_credentials=True`
- **Frontend ports**: Vite may use 5173 if 3000 is taken; update CORS_ORIGINS accordingly
- **v-html**: 사용자 입력을 v-html로 렌더링 시 반드시 DOMPurify 사용 (XSS 방지)
- **ESLint**: ESLint 9 flat config 사용 (`eslint.config.js`), 기존 `.eslintrc` 형식 사용 불가
- **Router Order**: `/clubs/create`가 `/clubs/:id`보다 먼저 정의되어야 함 (동적 라우트 우선순위)
- **Profile Completion**: 신규 사용자는 gender, birth_date 입력 전까지 프로필 완성 페이지로 리다이렉트됨
- **Timezone Bug**: JavaScript `toISOString()`은 UTC로 변환하여 KST 기준 날짜가 하루 밀릴 수 있음 → 로컬 날짜 컴포넌트 사용
- **Session Model**: `date`/`start_time`/`end_time`은 프로퍼티(KST), 실제 필드는 `start_datetime`/`end_datetime`(UTC)
- **API Response Fields**: 응답에 필요한 모든 필드를 포함했는지 확인 (예: `get_my_clubs`에 동호회 설정값 포함 필요)
- **Error Handling Pattern**: 프론트엔드에서 `error.response?.data?.detail || '기본 메시지'` 패턴 사용

## API Documentation

When backend is running: http://localhost:8000/docs

Key endpoints:
- `POST /api/auth/callback` - Cognito OAuth callback (sets cookie)
- `POST /api/auth/logout` - Clear auth cookie
- `GET /api/auth/me` - Current user info
- `POST /api/clubs/{club_id}/sessions/{id}/matches/generate` - Auto-generate matches
- `GET /api/clubs/{id}/seasons` - List seasons for a club

## Detailed Documentation

상세 문서는 `claudedocs/` 디렉토리를 참조하세요:
- [PROJECT_INDEX.md](./claudedocs/PROJECT_INDEX.md) - 프로젝트 종합 인덱스
- [BACKEND_ARCHITECTURE.md](./claudedocs/BACKEND_ARCHITECTURE.md) - 백엔드 아키텍처 상세
- [FRONTEND_ARCHITECTURE.md](./claudedocs/FRONTEND_ARCHITECTURE.md) - 프론트엔드 아키텍처 상세
- [API_REFERENCE.md](./claudedocs/API_REFERENCE.md) - API 엔드포인트 레퍼런스
- [DATA_MODEL.md](./claudedocs/DATA_MODEL.md) - 데이터 모델 및 관계
