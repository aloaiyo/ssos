# Repository Index (Compressed)

> 94% token reduction index for rapid context loading

## Quick Ref

**Stack**: FastAPI+Tortoise+PostgreSQL | Vue3+Vuetify3+Pinia | Cognito
**Core**: Auto match generation for fair game scheduling

## File Map

### Backend (`backend/app/`)

```
models/         # ORM
├── user.py          # User, cognito_sub
├── club.py          # Club (tenant)
├── member.py        # ClubMember (role: manager/member)
├── season.py        # Season, SeasonRanking
├── event.py         # Event, Session, SessionParticipant
├── match.py         # Match, MatchParticipant, MatchResult
├── guest.py         # Guest participants
├── ranking.py       # Ranking aggregation
├── fee.py           # Club fees
└── announcement.py  # Announcements

api/            # Routes
├── auth.py          # /auth/* (callback, logout, me) ★
├── clubs.py         # /clubs/*
├── members.py       # /clubs/{id}/members/*
├── sessions.py      # /clubs/{id}/sessions/* (largest, match gen) ★
├── seasons.py       # /clubs/{id}/seasons/*
├── matches.py       # /sessions/{id}/matches/*
├── rankings.py      # /clubs/{id}/rankings/*
├── guests.py        # Guest management
├── fees.py          # Fee management
├── announcements.py # Club announcements
└── ocr.py           # OCR result upload

services/       # Logic
├── matching_service.py     # Basic matching algo ★
├── ai_matching_service.py  # AI-based matching
├── auth_service.py         # Token exchange, user sync
├── cognito_service.py      # Cognito API wrapper
└── ocr_service.py          # Gemini OCR processing

core/           # Infrastructure
├── security.py      # JWT encode/decode
└── dependencies.py  # DI (get_current_user, require_club_manager, etc.)

config.py       # Settings, CORS, Tortoise config
main.py         # FastAPI app entry
```

### Frontend (`frontend/src/`)

```
views/          # Pages (31)
├── auth/            # Login, Register, Callback, ProfileCompletion
├── club/            # List, Detail, Create, Manage + tabs
├── member/          # List, Manage
├── session/         # List, Detail, Create
├── season/          # List, Detail
├── match/           # Schedule, Result, Upload, Generate
├── ranking/         # RankingView
├── profile/         # MyProfileView
├── HomeView.vue     # Dashboard (bento grid) ★
├── LandingView.vue  # Unauthenticated landing
└── NotFoundView.vue # 404

stores/         # Pinia (7)
├── auth.js          # user, isAuthenticated, isAdmin, checkAuth ★
├── club.js          # clubs, selectedClub, isManagerOfSelectedClub
├── member.js        # members, fetchMembers
├── session.js       # sessions
├── season.js        # seasons
├── match.js         # matches
└── ranking.js       # rankings

api/            # Axios clients (12)
├── index.js         # Base client, withCredentials:true ★
├── auth.js          # Cognito URLs, callback
├── clubs.js, members.js, sessions.js, seasons.js
├── matches.js, rankings.js, guests.js, events.js
├── ocr.js           # OCR upload
└── token.js         # Token utilities

components/     # Reusable (8)
├── layout/          # AppBar, NavigationDrawer, Footer
├── match/           # MatchCard, MatchSchedule
└── common/          # WeeklySchedulePicker, LoadingSpinner, ErrorAlert

router/index.js # Routes + guards (auth, profile completion)
utils/          # date.js, constants.js, validators.js
plugins/        # vuetify.js
```

## Enums

```python
MatchType: MENS_DOUBLES | WOMENS_DOUBLES | MIXED_DOUBLES | SINGLES
MemberRole: MANAGER | MEMBER | GUEST
ParticipantCategory: MEMBER | GUEST | ASSOCIATE
SeasonStatus: UPCOMING | ACTIVE | COMPLETED
```

## Key Patterns

### Auth Flow
```
Cognito UI → Code → Backend /auth/callback → JWT cookie → API calls
```

### Data Flow
```
View → Store → API → Backend → DB
View ← Store ← Response
```

### Multi-tenant
```
User → ClubMember → Club (boundary) → Season/Event/Session/Match
```

## Commands

```bash
# Backend
poetry run uvicorn app.main:app --reload     # :8000
poetry run aerich migrate --name "desc"
poetry run aerich upgrade
poetry run pytest

# Frontend
npm run dev          # :3000
npm run build
npm run lint:fix
```

## Gotchas

- Tortoise: ALL ops need `await` (.count(), .exists())
- Pydantic V2: `ConfigDict(from_attributes=True)`
- Cookies: `withCredentials: true` + CORS credentials
- v-html: DOMPurify required
- Router: `/clubs/create` before `/clubs/:id`
- Profile: Redirect to completion if missing gender/birth_date

---
*Compressed index for token efficiency*
