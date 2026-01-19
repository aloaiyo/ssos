# Project Index: 테니스 동호회 관리 시스템 (SSOS)

**Generated**: 2026-01-19
**Tech Stack**: FastAPI + Tortoise-ORM + PostgreSQL | Vue 3 + Vuetify 3 + Pinia | AWS Cognito
**Total Lines**: 25,792 (Backend: 8,030 | Frontend: 17,762)

---

## Project Structure

```
ssos/
├── backend/                    # FastAPI Backend (48 files, 8,030 lines)
│   ├── app/
│   │   ├── main.py            # Entry point
│   │   ├── config.py          # Settings + AWS SSM
│   │   ├── models/            # 13 Tortoise-ORM models
│   │   ├── schemas/           # 9 Pydantic V2 schemas
│   │   ├── api/               # 14 FastAPI routers (80+ endpoints)
│   │   ├── services/          # 5 business logic services
│   │   └── core/              # security, dependencies
│   └── migrations/            # Aerich DB migrations
│
├── frontend/                   # Vue 3 Frontend (64 files, 17,762 lines)
│   └── src/
│       ├── main.js            # Entry point
│       ├── views/             # 31 page components
│       ├── components/        # 8 reusable components
│       ├── stores/            # 7 Pinia stores (1,364 lines)
│       ├── api/               # 12 API clients (876 lines)
│       ├── router/            # Vue Router (42 routes)
│       └── utils/             # date.js, validators.js
│
├── claudedocs/                # Claude documentation (5 files)
└── .github/workflows/         # CI/CD (GitHub Actions)
```

---

## Entry Points

| Type | Path | Description |
|------|------|-------------|
| Backend API | `backend/app/main.py` | FastAPI app, CORS, routers |
| Frontend App | `frontend/src/main.js` | Vue 3 app, plugins |
| Config | `backend/app/config.py` | Environment settings |
| Router | `frontend/src/router/index.js` | Vue Router (42 routes) |

---

## Core Modules

### Backend Services (5)
| Module | Path | Purpose |
|--------|------|---------|
| matching_service | `app/services/matching_service.py` | **Core**: Auto match generation |
| ai_matching_service | `app/services/ai_matching_service.py` | AI-powered intelligent matching |
| auth_service | `app/services/auth_service.py` | Cognito token exchange |
| cognito_service | `app/services/cognito_service.py` | AWS Cognito API wrapper |
| ocr_service | `app/services/ocr_service.py` | Score image OCR (Gemini AI) |

### Backend Models (13)
| Model | Key Fields |
|-------|------------|
| User | email, cognito_sub, role, subscription_tier |
| Club | name, location, created_by |
| ClubMember | club, user, role, status, gender |
| Season | club, name, start_date, end_date, status |
| SeasonRanking | season, club_member, points, rank |
| Session | event, season, date, start_time, num_courts |
| SessionParticipant | session, club_member/guest/user, category |
| Match | session, match_type, court, status |
| MatchParticipant | match, club_member/guest/user, team |
| MatchResult | match, team_a_score, team_b_score, winner |
| Guest | club, name, gender |
| Ranking | club, club_member, points |
| Announcement, Fee, Schedule | auxiliary models |

### Backend API Routers (14)
| Router | Prefix | Key Endpoints |
|--------|--------|---------------|
| auth | /api/auth | callback, logout, me, refresh |
| clubs | /api/clubs | CRUD, join, leave |
| members | /api/clubs/{id}/members | approve, role change |
| guests | /api/clubs/{id}/guests | CRUD, link to member |
| seasons | /api/clubs/{id}/seasons | CRUD, rankings |
| sessions | /api/clubs/{id}/sessions | CRUD, participants, **generate**, **generate-ai** |
| matches | /api/matches | CRUD, result |
| rankings | /api/clubs/{id}/rankings | list, calculate |
| announcements | /api/clubs/{id}/announcements | CRUD |
| fees | /api/clubs/{id}/fees | settings, payments |
| events | /api/clubs/{id}/events | CRUD |
| users | /api/users | me/clubs |
| ocr | /api/ocr | extract, save-matches |

### Frontend Stores (7)
| Store | Lines | Key State | Key Actions |
|-------|-------|-----------|-------------|
| auth | 244 | user, isAuthenticated | login, logout, handleCallback |
| club | 222 | clubs, selectedClubId | fetchClubs, selectClub |
| session | 279 | sessions, participants | fetchSessions, addParticipant |
| season | 209 | seasons, rankings | fetchSeasons, calculateRankings |
| match | 168 | matches, currentMatch | generateMatches, recordResult |
| member | 148 | members | fetchMembers, updateRole |
| ranking | 94 | rankings | fetchRankings |

### Frontend Views (31)
| Category | Views |
|----------|-------|
| Auth (5) | Login, Register, VerifyEmail, Callback, ProfileCompletion |
| Club (10) | List, Detail, Create, Manage + 6 tabs (Info, Members, Sessions, Announcements, Fees, Stats) |
| Season (2) | List, Detail |
| Session (3) | List, Detail, Create |
| Match (4) | Schedule, Generate, Result, Upload |
| Member (2) | List, Manage |
| Ranking (1) | View |
| Other (4) | Landing, Home, Profile, NotFound |

---

## Key Patterns

### Authentication Flow
```
Frontend → Cognito Hosted UI → Authorization Code
Backend /api/auth/callback → ID Token → HTTP-only Cookie
Frontend API calls include cookie automatically (withCredentials: true)
```

### Multi-Tenant
- Club = tenant boundary
- All queries filter by `club_id`
- Soft delete with `is_deleted` flag

### Participant Categories
```python
MEMBER    → club_member (정회원)
GUEST     → guest (미가입 외부인)
ASSOCIATE → user (준회원)
```

### Match Types
```python
MENS_DOUBLES     # 남복: 4명 2v2
WOMENS_DOUBLES   # 여복: 4명 2v2
MIXED_DOUBLES    # 혼복: 남녀 페어링
SINGLES          # 단식: 2명 1v1
```

### Security Patterns
- XSS Prevention: DOMPurify for v-html content
- Production Build: console.log auto-removal (vite esbuild.drop)
- ESLint: no-console warn, vue/no-v-html warn

---

## Configuration

| File | Purpose |
|------|---------|
| `backend/pyproject.toml` | Poetry deps, Aerich config |
| `backend/.env` | DB, JWT, Cognito settings |
| `frontend/package.json` | npm deps, scripts |
| `frontend/.env` | API URL, Cognito settings |
| `frontend/vite.config.js` | Vite build config |
| `frontend/eslint.config.js` | ESLint 9 flat config |

---

## Quick Start

```bash
# Backend
cd backend && poetry install
createdb tennis_club
poetry run aerich init-db
poetry run uvicorn app.main:app --reload  # :8000

# Frontend
cd frontend && npm install
npm run dev  # :3000

# Both at once
./start_dev.sh
```

---

## Key Dependencies

### Backend (Python 3.11+)
| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | ^0.109.0 | Web framework |
| tortoise-orm | ^0.20.0 | Async ORM |
| aerich | ^0.7.2 | DB migrations |
| pydantic | ^2.5.0 | Data validation |
| boto3 | ^1.34.0 | AWS SDK |
| python-jose | ^3.3.0 | JWT handling |
| google-genai | ^1.59.0 | Gemini AI (OCR) |

### Frontend (Node.js)
| Package | Version | Purpose |
|---------|---------|---------|
| vue | ^3.4.21 | UI framework |
| vuetify | ^3.5.7 | Material Design UI |
| pinia | ^2.1.7 | State management |
| vue-router | ^4.3.0 | Client routing |
| axios | ^1.6.7 | HTTP client |
| dayjs | ^1.11.10 | Date handling |
| dompurify | ^3.3.1 | XSS prevention |
| eslint | ^9.39.2 | Code linting |

---

## Development Status

| Phase | Status | Features |
|-------|--------|----------|
| 1 | **Done** | Auth, Club CRUD, Members, Layout |
| 2 | **Done** | Season, Session, Match, Ranking, AI Matching, OCR |
| 3 | Planned | Algorithm optimization, Drag & Drop, Advanced Stats |

---

## Documentation

| Document | Path | Purpose |
|----------|------|---------|
| CLAUDE.md | `/CLAUDE.md` | Claude Code guide |
| PROJECT_INDEX | `/claudedocs/PROJECT_INDEX.md` | Project index |
| BACKEND_ARCHITECTURE | `/claudedocs/BACKEND_ARCHITECTURE.md` | Backend details |
| FRONTEND_ARCHITECTURE | `/claudedocs/FRONTEND_ARCHITECTURE.md` | Frontend details |
| API_REFERENCE | `/claudedocs/API_REFERENCE.md` | API endpoints |
| DATA_MODEL | `/claudedocs/DATA_MODEL.md` | Database models |

---

*Index size: ~3KB | Full codebase read: ~58KB (94% token reduction)*
