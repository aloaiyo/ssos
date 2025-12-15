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
npm run lint     # Linting
```

## Architecture

### Authentication Flow (AWS Cognito)

The system uses **AWS Cognito** for authentication with a dual-token approach:

1. **Cognito Hosted UI** handles login/signup (Google SSO supported)
2. Backend exchanges Cognito tokens for **local JWT tokens**
3. Frontend stores local JWT in localStorage, auto-refreshes on 401

```
Frontend → Cognito Hosted UI → Authorization Code
    ↓
Backend /api/auth/callback → Exchange code for Cognito ID Token
    ↓
Verify ID Token → Sync/Create local User → Issue local JWT
    ↓
Frontend uses local JWT for all subsequent API calls
```

**Key files**:
- `backend/app/services/cognito_service.py` - Cognito API wrapper
- `backend/app/services/auth_service.py` - Token exchange, user sync
- `frontend/src/api/auth.js` - Cognito redirect URLs, API calls
- `frontend/src/views/auth/CallbackView.vue` - OAuth callback handler

### Multi-Tenant Data Model

```
User (전역 사용자, cognito_sub linked)
  └── ClubMember (동호회 회원, role: admin/member)
        └── Club (동호회) ← tenant isolation boundary
              ├── Event (일정)
              │     └── Session (세션)
              │           ├── SessionParticipant
              │           └── Match (경기)
              │                 └── MatchParticipant
              │                       └── MatchResult
              └── Ranking
```

**Important**: All club-related queries MUST filter by `club_id` for tenant isolation.

### Backend Structure

```
backend/app/
├── models/       # Tortoise-ORM models (user.py, club.py, member.py, event.py, match.py, ranking.py)
├── schemas/      # Pydantic V2 schemas
├── api/          # FastAPI routes (auth, clubs, members, events, sessions, matches, rankings, users)
├── services/     # Business logic (auth_service, cognito_service, matching_service)
├── core/         # security.py (JWT), dependencies.py (DI)
└── config.py     # Settings with AWS SSM support
```

### Frontend Structure

```
frontend/src/
├── views/        # Page components (auth/, club/, member/, session/, match/, ranking/)
├── components/   # Reusable (layout/, common/, match/)
├── stores/       # Pinia stores (auth, club, member, session, match, ranking)
├── api/          # Axios clients (index.js has interceptors for auth)
├── router/       # Vue Router with auth guards
└── plugins/      # Vuetify config
```

## Core Algorithm: Match Generation

**Location**: `backend/app/services/matching_service.py`

Generates fair game schedules from session participants:
1. Group by match type (mens_doubles, mixed_doubles, singles)
2. Gender pairing for mixed doubles
3. Random shuffle for fairness
4. Court allocation and time scheduling

**Match Types**:
- `MENS_DOUBLES` (남복): 4 male (2v2)
- `MIXED_DOUBLES` (혼복): 2 male + 2 female (1m+1f vs 1m+1f)
- `SINGLES` (단식): 2 players (1v1)

## Development Patterns

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

### API Interceptors
`frontend/src/api/index.js` handles:
- Auto-attach JWT to requests
- 401 response → auto-refresh token via `/api/auth/refresh`
- Failed refresh → logout and redirect to login

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

## Common Gotchas

- **Aerich**: Run `migrate` before `upgrade` after model changes
- **Tortoise**: ALL db operations need `await`, even `.count()`, `.exists()`
- **Pydantic V2**: Use `model_config = ConfigDict(from_attributes=True)`
- **Cognito tokens**: Backend issues local JWTs after Cognito validation; frontend only uses local tokens
- **CORS**: Backend 8000, Frontend 3000 - configured in `config.py`
- **Frontend ports**: Vite may use 5173 if 3000 is taken; check CORS_ORIGINS

## API Documentation

When backend is running: http://localhost:8000/docs

Key endpoints:
- `POST /api/auth/login` - Email/password login
- `POST /api/auth/callback` - Cognito OAuth callback
- `POST /api/auth/refresh` - Token refresh
- `GET /api/auth/me` - Current user info
- `POST /api/sessions/{id}/matches/generate` - Auto-generate matches
