# 테니스 동호회 관리 시스템 - 백엔드

FastAPI + Tortoise-ORM을 사용한 테니스 동호회 관리 시스템의 백엔드 API

## 기술 스택

- **Python**: 3.11+
- **FastAPI**: 최신 버전
- **Tortoise-ORM**: 비동기 ORM
- **PostgreSQL**: 데이터베이스
- **Aerich**: 데이터베이스 마이그레이션
- **JWT**: 인증/인가
- **Poetry**: 의존성 관리

## 프로젝트 구조

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 앱 엔트리포인트
│   ├── config.py              # 설정 관리
│   ├── models/                # Tortoise-ORM 모델
│   │   ├── user.py           # 사용자 모델
│   │   ├── club.py           # 동호회 모델
│   │   ├── member.py         # 회원 모델
│   │   ├── event.py          # 일정/세션 모델
│   │   ├── match.py          # 매칭/결과 모델
│   │   └── ranking.py        # 랭킹 모델
│   ├── schemas/              # Pydantic 스키마
│   ├── api/                  # API 라우터
│   │   ├── auth.py          # 인증 API
│   │   ├── clubs.py         # 동호회 API
│   │   ├── members.py       # 회원 API
│   │   ├── events.py        # 일정 API
│   │   ├── sessions.py      # 세션 API
│   │   ├── matches.py       # 매칭 API
│   │   └── rankings.py      # 랭킹 API
│   ├── services/            # 비즈니스 로직
│   │   ├── auth_service.py
│   │   └── matching_service.py
│   └── core/                # 핵심 유틸리티
│       ├── security.py      # JWT, 비밀번호 해싱
│       └── dependencies.py  # 의존성 주입
├── migrations/              # Aerich 마이그레이션
├── pyproject.toml          # Poetry 설정
├── .env                    # 환경 변수 (gitignore)
└── README.md
```

## 설치 및 실행

### 1. 의존성 설치

```bash
cd backend
poetry install
```

### 2. 환경 변수 설정

`.env.example`을 복사하여 `.env` 파일 생성:

```bash
cp .env.example .env
```

`.env` 파일 수정:

```env
DATABASE_URL=postgres://postgres:password@localhost:5432/tennis_club
SECRET_KEY=your-super-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. 데이터베이스 설정

PostgreSQL 데이터베이스 생성:

```bash
createdb tennis_club
```

### 4. 마이그레이션 초기화

```bash
poetry run aerich init -t app.config.TORTOISE_ORM
poetry run aerich init-db
```

### 5. 서버 실행

```bash
poetry run uvicorn app.main:app --reload
```

또는:

```bash
poetry run python -m app.main
```

서버가 실행되면 다음 URL에서 접속 가능:
- API: http://localhost:8000
- API 문서 (Swagger): http://localhost:8000/docs
- API 문서 (ReDoc): http://localhost:8000/redoc

## API 엔드포인트

### 인증 (Auth)
- `POST /api/auth/register` - 회원가입
- `POST /api/auth/login` - 로그인
- `GET /api/auth/me` - 현재 사용자 정보

### 동호회 (Clubs)
- `GET /api/clubs` - 동호회 목록
- `POST /api/clubs` - 동호회 생성
- `GET /api/clubs/{club_id}` - 동호회 상세
- `PUT /api/clubs/{club_id}` - 동호회 수정
- `DELETE /api/clubs/{club_id}` - 동호회 삭제

### 회원 (Members)
- `GET /api/clubs/{club_id}/members` - 회원 목록
- `POST /api/clubs/{club_id}/members` - 회원 추가
- `GET /api/clubs/{club_id}/members/{member_id}` - 회원 상세
- `PUT /api/clubs/{club_id}/members/{member_id}` - 회원 수정
- `DELETE /api/clubs/{club_id}/members/{member_id}` - 회원 제거

### 일정 (Events)
- `GET /api/events?club_id={club_id}` - 일정 목록
- `POST /api/events` - 일정 생성
- `GET /api/events/{event_id}` - 일정 상세
- `PUT /api/events/{event_id}` - 일정 수정
- `DELETE /api/events/{event_id}` - 일정 삭제

### 세션 (Sessions)
- `GET /api/sessions?event_id={event_id}` - 세션 목록
- `POST /api/sessions` - 세션 생성
- `GET /api/sessions/{session_id}` - 세션 상세
- `PUT /api/sessions/{session_id}` - 세션 수정
- `DELETE /api/sessions/{session_id}` - 세션 삭제
- `GET /api/sessions/{session_id}/participants` - 세션 참가자 목록
- `POST /api/sessions/{session_id}/participants` - 세션 참가자 추가

### 매칭 (Matches)
- `GET /api/matches?session_id={session_id}` - 매치 목록
- `POST /api/matches` - 매치 생성
- `GET /api/matches/{match_id}` - 매치 상세
- `PUT /api/matches/{match_id}` - 매치 수정
- `DELETE /api/matches/{match_id}` - 매치 삭제
- `GET /api/matches/{match_id}/participants` - 매치 참가자 목록
- `POST /api/matches/{match_id}/result` - 매치 결과 등록
- `GET /api/matches/{match_id}/result` - 매치 결과 조회

### 랭킹 (Rankings)
- `GET /api/rankings?club_id={club_id}` - 랭킹 목록
- `GET /api/rankings/{ranking_id}` - 랭킹 상세

## 데이터베이스 마이그레이션

### 새로운 마이그레이션 생성

```bash
poetry run aerich migrate --name "migration_name"
```

### 마이그레이션 적용

```bash
poetry run aerich upgrade
```

### 마이그레이션 롤백

```bash
poetry run aerich downgrade
```

### 마이그레이션 히스토리

```bash
poetry run aerich history
```

## 개발

### 코드 스타일

프로젝트는 다음 컨벤션을 따릅니다:
- PEP 8 스타일 가이드
- 타입 힌트 필수
- 한글 주석 사용

### 테스트

```bash
poetry run pytest
```

## 주요 기능

### 1. 인증/인가
- JWT 기반 토큰 인증
- 비밀번호 해싱 (bcrypt)
- 역할 기반 접근 제어 (RBAC)

### 2. 동호회 관리
- 동호회 생성/수정/삭제
- 회원 관리
- 역할 관리 (관리자/회원)

### 3. 일정/세션 관리
- 일정 생성 (정기/특별)
- 세션 생성 및 설정
- 참가자 관리

### 4. 매칭 시스템
- 자동 매칭 알고리즘
- 복식/혼합복식/단식 지원
- 코트 배정 및 시간 스케줄링

### 5. 결과 및 랭킹
- 경기 결과 기록
- 자동 랭킹 계산
- 승률 통계

## 환경 변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| DATABASE_URL | PostgreSQL 연결 URL | postgres://postgres:password@localhost:5432/tennis_club |
| SECRET_KEY | JWT 시크릿 키 | (필수) |
| ALGORITHM | JWT 알고리즘 | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | 토큰 만료 시간 (분) | 30 |
| APP_NAME | 애플리케이션 이름 | Tennis Club Management System |
| DEBUG | 디버그 모드 | True |
| CORS_ORIGINS | CORS 허용 OriginFastAPI 시작하기 | http://localhost:5173 |

## 라이센스

MIT License
