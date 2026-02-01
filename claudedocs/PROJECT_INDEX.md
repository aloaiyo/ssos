# 프로젝트 인덱스

> 테니스 동호회 관리 시스템 - 종합 프로젝트 문서

## 프로젝트 개요

**Tech Stack**: FastAPI + Tortoise-ORM + PostgreSQL | Vue 3 + Vuetify 3 + Pinia | AWS Cognito

**핵심 기능**: 자동 경기 매칭 생성으로 공정한 게임 스케줄링

---

## 문서 목록

| 문서 | 설명 |
|------|------|
| [BACKEND_ARCHITECTURE.md](./BACKEND_ARCHITECTURE.md) | 백엔드 아키텍처 상세 |
| [FRONTEND_ARCHITECTURE.md](./FRONTEND_ARCHITECTURE.md) | 프론트엔드 아키텍처 상세 |
| [API_REFERENCE.md](./API_REFERENCE.md) | API 엔드포인트 레퍼런스 |
| [DATA_MODEL.md](./DATA_MODEL.md) | 데이터 모델 및 관계 |

---

## 빠른 참조

### 디렉토리 구조

```
ssos/
├── backend/
│   └── app/
│       ├── models/      # 13개 Tortoise-ORM 모델
│       ├── schemas/     # 9개 Pydantic V2 스키마
│       ├── api/         # 14개 FastAPI 라우터
│       ├── services/    # 5개 비즈니스 로직 서비스
│       └── core/        # 보안 및 의존성 주입
│
├── frontend/
│   └── src/
│       ├── views/       # 31개 페이지 컴포넌트
│       ├── stores/      # 7개 Pinia 스토어
│       ├── api/         # 12개 API 클라이언트
│       ├── components/  # 8개 재사용 컴포넌트
│       ├── utils/       # 2개 유틸리티 모듈
│       └── router/      # Vue Router 설정
│
└── CLAUDE.md            # Claude Code 가이드
```

### 핵심 파일 위치

| 기능 | 파일 |
|------|------|
| 매칭 알고리즘 | `backend/app/services/matching_service.py`, `ai_matching_service.py` |
| 인증 흐름 | `backend/app/services/auth_service.py`, `cognito_service.py` |
| 권한 체크 | `backend/app/core/dependencies.py` |
| OCR 처리 | `backend/app/services/ocr_service.py` |
| API 클라이언트 | `frontend/src/api/index.js` |
| 라우팅 | `frontend/src/router/index.js` |
| 메인 레이아웃 | `frontend/src/components/layout/` |
| 홈 대시보드 | `frontend/src/views/HomeView.vue` |

### 주요 Enum 값

```python
# 경기 타입
MatchType: MENS_DOUBLES, MIXED_DOUBLES, SINGLES, WOMENS_DOUBLES

# 회원 역할
MemberRole: MANAGER, MEMBER, GUEST

# 참가자 카테고리
ParticipantCategory: MEMBER, GUEST, ASSOCIATE

# 시즌 상태
SeasonStatus: UPCOMING, ACTIVE, COMPLETED
```

### 개발 명령어

```bash
# Backend
cd backend
poetry run uvicorn app.main:app --reload
poetry run aerich migrate --name "description"
poetry run aerich upgrade
poetry run pytest
poetry run black .
poetry run isort .

# Frontend
cd frontend
npm run dev
npm run build
npm run lint        # ESLint 검사
npm run lint:fix    # ESLint 자동 수정
```

---

## 아키텍처 다이어그램

### 인증 흐름
```
Frontend → Cognito Hosted UI → Authorization Code
    ↓
Backend /api/auth/callback → Exchange code for Cognito ID Token
    ↓
Verify ID Token → Sync/Create local User → Set HTTP-only cookie
    ↓
Frontend API calls include cookie automatically
```

### 데이터 흐름
```
View Component → Store Action → API Client → Backend → DB
                                    ↓
View (reactive) ← Store State ← Response
```

### 멀티테넌트 구조
```
User (전역)
  └── ClubMember
        └── Club (테넌트 경계)
              ├── Season → SeasonRanking
              ├── Event → Session → Match
              ├── Guest
              └── Announcement, Fee
```

---

## 개발 상태

### Phase 1 (완료)
- 인증 시스템 (AWS Cognito + HTTP-only 쿠키)
- 동호회 CRUD
- 회원 관리
- 기본 UI 레이아웃

### Phase 2 (완료)
- 시즌 관리
- 세션 생성 및 참가자 관리
- 자동 매칭 알고리즘 (기본 + AI)
- 경기 결과 입력
- 랭킹 시스템
- 여복(WOMENS_DOUBLES) 지원
- 코드 품질 개선 (ESLint, DOMPurify)

### Phase 3 (진행중)
- OCR 경기 결과 업로드 개선 (시즌/세션 생성, 선수 매핑)
- 타임존 처리 개선 (UTC 저장, KST 표시)
- 캘린더 UX 개선 (빈 날짜 클릭 → 세션 생성)
- 동호회 기본 설정값 연동

### Phase 4 (예정)
- 매칭 알고리즘 최적화
- 드래그 앤 드롭 매칭 수정
- 고급 통계 대시보드

---

## 보안 패턴

### XSS 방지
- `v-html` 사용 시 DOMPurify로 sanitize 필수
- ESLint `vue/no-v-html` 경고 규칙 적용

### Production 빌드
- `console.log` 자동 제거 (vite esbuild.drop)
- ESLint `no-console` 경고 규칙

---

## 주요 Gotcha

| 이슈 | 원인 | 해결 |
|------|------|------|
| 날짜가 하루 밀림 | JS `toISOString()`이 UTC로 변환 | 로컬 날짜 컴포넌트 사용 |
| Session 생성 에러 | `date`/`start_time` 대신 `start_datetime` 필요 | UTC datetime으로 변환 |
| 동호회 설정값 안 뜸 | `get_my_clubs` API에 필드 누락 | 응답에 설정 필드 추가 |
| 에러 메시지 안 뜸 | 프론트엔드 catch 블록 | `error.response?.data?.detail` 사용 |

---

*Last Updated: 2026-02-01*
