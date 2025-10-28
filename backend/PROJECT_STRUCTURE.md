# 프로젝트 구조

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI 애플리케이션 엔트리포인트
│   ├── config.py                    # 설정 관리 (환경 변수, Tortoise ORM 설정)
│   │
│   ├── models/                      # Tortoise-ORM 데이터베이스 모델
│   │   ├── __init__.py
│   │   ├── user.py                  # User 모델 (전역 사용자)
│   │   ├── club.py                  # Club 모델 (동호회)
│   │   ├── member.py                # ClubMember 모델 (동호회 회원)
│   │   ├── event.py                 # Event, SessionConfig, Session, SessionParticipant 모델
│   │   ├── match.py                 # Match, MatchParticipant, MatchResult 모델
│   │   └── ranking.py               # Ranking 모델
│   │
│   ├── schemas/                     # Pydantic 스키마 (요청/응답 검증)
│   │   ├── __init__.py
│   │   ├── user.py                  # 사용자 스키마
│   │   ├── club.py                  # 동호회 스키마
│   │   ├── member.py                # 회원 스키마
│   │   ├── event.py                 # 일정/세션 스키마
│   │   ├── match.py                 # 매치 스키마
│   │   └── ranking.py               # 랭킹 스키마
│   │
│   ├── api/                         # API 라우터 (엔드포인트)
│   │   ├── __init__.py
│   │   ├── auth.py                  # 인증 API (login, register, me)
│   │   ├── clubs.py                 # 동호회 CRUD API
│   │   ├── members.py               # 회원 관리 API
│   │   ├── events.py                # 일정 관리 API
│   │   ├── sessions.py              # 세션 관리 API
│   │   ├── matches.py               # 매치 관리 API
│   │   └── rankings.py              # 랭킹 조회 API
│   │
│   ├── services/                    # 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── auth_service.py          # 인증 서비스 (JWT, 비밀번호)
│   │   └── matching_service.py      # 매칭 알고리즘 (자동 매치 생성)
│   │
│   └── core/                        # 핵심 유틸리티
│       ├── __init__.py
│       ├── security.py              # JWT 토큰, 비밀번호 해싱
│       └── dependencies.py          # FastAPI 의존성 주입 (현재 사용자 등)
│
├── migrations/                      # Aerich 데이터베이스 마이그레이션
│
├── pyproject.toml                   # Poetry 의존성 관리
├── .env                             # 환경 변수 (DB 연결, JWT 비밀키 등)
├── .env.example                     # 환경 변수 예시
├── .gitignore                       # Git 무시 파일 목록
├── README.md                        # 프로젝트 개요 및 사용법
├── SETUP.md                         # 빠른 시작 가이드
└── PROJECT_STRUCTURE.md             # 이 파일
```

## 데이터베이스 스키마

### 주요 테이블

1. **users** - 전역 사용자
   - 이메일, 비밀번호, 이름
   - 슈퍼 관리자 플래그

2. **clubs** - 동호회
   - 이름, 설명
   - 생성자 (FK → users)

3. **club_members** - 동호회 회원
   - 동호회 (FK → clubs)
   - 사용자 (FK → users)
   - 역할 (admin/member)
   - 성별, 선호 경기 타입

4. **events** - 일정
   - 동호회 (FK → clubs)
   - 제목, 타입 (정기/특별)
   - 반복 규칙

5. **session_configs** - 세션 설정 템플릿
   - 동호회 (FK → clubs)
   - 코트 수, 경기 시간 등

6. **sessions** - 세션 (실제 경기 일정)
   - 일정 (FK → events)
   - 날짜, 시작/종료 시간
   - 상태 (draft/confirmed/completed)

7. **session_participants** - 세션 참가자
   - 세션 (FK → sessions)
   - 회원 (FK → club_members)
   - 참가 타입

8. **matches** - 경기
   - 세션 (FK → sessions)
   - 코트 번호, 시간
   - 상태

9. **match_participants** - 경기 참가자
   - 경기 (FK → matches)
   - 회원 (FK → club_members)
   - 팀 (A/B), 포지션

10. **match_results** - 경기 결과
    - 경기 (FK → matches)
    - 점수, 승자

11. **rankings** - 랭킹
    - 동호회 (FK → clubs)
    - 회원 (FK → club_members)
    - 전적, 포인트

## API 계층 구조

```
Client Request
    ↓
FastAPI Router (api/)
    ↓
Dependencies (core/dependencies.py) - 인증 확인
    ↓
Service Layer (services/) - 비즈니스 로직
    ↓
ORM Models (models/) - 데이터베이스 접근
    ↓
PostgreSQL Database
    ↓
Response (schemas/) - Pydantic 검증
    ↓
Client Response
```

## 주요 기능 흐름

### 1. 사용자 인증
```
POST /api/auth/login
→ auth.py (router)
→ auth_service.authenticate_user()
→ security.verify_password()
→ auth_service.create_user_token()
→ JWT Token 반환
```

### 2. 동호회 생성
```
POST /api/clubs
→ clubs.py (router)
→ get_current_active_user() (dependency)
→ Club.create() (ORM)
→ ClubResponse 반환
```

### 3. 매치 생성
```
세션 참가자 등록
→ POST /api/sessions/{id}/participants
→ SessionParticipant 생성

매치 자동 생성
→ matching_service.create_matches_for_session()
→ 참가자를 타입별로 분류
→ 알고리즘에 따라 매치 생성
→ Match + MatchParticipant 생성
```

## 환경 설정

### 필수 환경 변수 (.env)
- `DATABASE_URL`: PostgreSQL 연결 문자열
- `SECRET_KEY`: JWT 서명용 비밀키
- `ACCESS_TOKEN_EXPIRE_MINUTES`: 토큰 만료 시간
- `CORS_ORIGINS`: CORS 허용 도메인

## 개발 워크플로우

1. 모델 수정 (models/)
2. 스키마 추가/수정 (schemas/)
3. 서비스 로직 구현 (services/)
4. API 라우터 작성 (api/)
5. 마이그레이션 생성 (`aerich migrate`)
6. 마이그레이션 적용 (`aerich upgrade`)
7. 테스트
8. 커밋

## 보안 고려사항

- ✅ JWT 기반 인증
- ✅ 비밀번호 bcrypt 해싱
- ✅ CORS 설정
- ✅ 환경 변수로 민감 정보 관리
- ✅ SQL Injection 방지 (ORM 사용)
- ✅ 역할 기반 접근 제어

## 성능 최적화

- 비동기 I/O (FastAPI + Tortoise-ORM)
- 데이터베이스 인덱스 (unique, FK)
- 페이지네이션 (skip/limit)
- Prefetch related (N+1 쿼리 방지)

## 향후 개선 사항

- [ ] 캐싱 (Redis)
- [ ] 백그라운드 작업 (Celery)
- [ ] 웹소켓 (실시간 매치 업데이트)
- [ ] 파일 업로드 (프로필 사진)
- [ ] 이메일 알림
- [ ] 로깅 및 모니터링
- [ ] API Rate Limiting
- [ ] 데이터베이스 백업 전략
