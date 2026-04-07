<!-- Generated: 2026-04-07 -->

# SSOS - 테니스 동호회 관리 시스템

## Purpose
테니스 동호회 운영을 위한 풀스택 웹 서비스. 회원 관리, 세션/경기 자동 생성, 랭킹, 회비 관리 등을 제공한다. FastAPI 백엔드 + Vue 3 프론트엔드 구조.

## Key Files
| File | Description |
|------|-------------|
| `CLAUDE.md` | AI 에이전트 프로젝트 가이드 (아키텍처, 패턴, 명령어) |
| `start_dev.sh` | 백엔드+프론트엔드 동시 실행 스크립트 |
| `README.md` | 프로젝트 소개 |

## Subdirectories
| Directory | Purpose |
|-----------|---------|
| `backend/` | FastAPI + Tortoise-ORM 백엔드 (see `backend/AGENTS.md`) |
| `frontend/` | Vue 3 + Vuetify 3 프론트엔드 (see `frontend/AGENTS.md`) |
| `.github/workflows/` | CI/CD 배포 워크플로우 (see `.github/AGENTS.md`) |
| `claudedocs/` | 프로젝트 상세 문서 |

## For AI Agents

### Working In This Directory
- `CLAUDE.md`를 반드시 먼저 읽고 프로젝트 컨텍스트를 파악할 것
- 멀티 테넌트: 모든 DB 쿼리에 `club_id` 필터 필수
- 타임존: 백엔드 UTC 저장 → KST 변환 응답, 프론트엔드 로컬 날짜 사용
- 인증: AWS Cognito + HTTP-only 쿠키 방식

### Testing Requirements
- 백엔드: `cd backend && poetry run pytest`
- 프론트엔드: `cd frontend && npm run lint`

### Common Patterns
- Pydantic V2 (`ConfigDict(from_attributes=True)`)
- Tortoise-ORM 비동기 (`await` 필수)
- Vue 3 Composition API (`<script setup>`)
- Vuetify 3 컴포넌트 라이브러리

## Dependencies
### External
- Python 3.11+, Poetry
- Node.js 18+, npm
- PostgreSQL
- AWS Cognito (인증)
- Google Gemini API (OCR)

<!-- MANUAL: -->
