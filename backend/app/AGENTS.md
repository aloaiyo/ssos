<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-07 -->

# app

## Purpose
백엔드 애플리케이션 패키지. FastAPI 앱 인스턴스, 라우터, 모델, 서비스, 스키마를 포함한다.

## Key Files
| File | Description |
|------|-------------|
| `main.py` | FastAPI 앱 생성, 라우터 등록, CORS, Tortoise 초기화 |
| `config.py` | Settings 클래스 (환경변수, AWS SSM, CORS_ORIGINS) |

## Subdirectories
| Directory | Purpose |
|-----------|---------|
| `api/` | FastAPI 라우터 (REST API 엔드포인트) (see `api/AGENTS.md`) |
| `core/` | 인증, 보안, 타임존 유틸리티 (see `core/AGENTS.md`) |
| `models/` | Tortoise-ORM 데이터 모델 (see `models/AGENTS.md`) |
| `schemas/` | Pydantic V2 요청/응답 스키마 (see `schemas/AGENTS.md`) |
| `services/` | 비즈니스 로직 서비스 (see `services/AGENTS.md`) |

## For AI Agents

### Working In This Directory
- `main.py` 수정 시 라우터 등록 순서 확인
- `config.py`의 CORS_ORIGINS에 프론트엔드 포트 포함 확인

<!-- MANUAL: -->
