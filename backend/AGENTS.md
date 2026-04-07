<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-07 -->

# Backend

## Purpose
FastAPI 기반 REST API 서버. Tortoise-ORM으로 PostgreSQL 연동, AWS Cognito 인증, 경기 자동 매칭 알고리즘, OCR 결과 처리 등 핵심 비즈니스 로직을 담당한다.

## Key Files
| File | Description |
|------|-------------|
| `pyproject.toml` | Poetry 의존성 및 프로젝트 설정 |
| `reset_db.py` | DB 초기화 스크립트 |

## Subdirectories
| Directory | Purpose |
|-----------|---------|
| `app/` | 애플리케이션 소스 코드 (see `app/AGENTS.md`) |
| `migrations/` | Aerich DB 마이그레이션 (see `migrations/AGENTS.md`) |
| `tests/` | pytest 테스트 (see `tests/AGENTS.md`) |

## For AI Agents

### Working In This Directory
- `poetry install`로 의존성 설치
- DB 변경 시 `poetry run aerich migrate --name "설명"` → `aerich upgrade`
- 모든 Tortoise-ORM 호출에 `await` 필수 (`.count()`, `.exists()` 포함)

### Testing Requirements
```bash
poetry run pytest                    # 전체 테스트
poetry run pytest --cov=app          # 커버리지
poetry run pytest tests/test_matching_service.py  # 단일
```

### Common Patterns
- Pydantic V2: `ConfigDict(from_attributes=True)`
- UTC 저장 / KST 응답: `from app.core.timezone import to_utc, to_kst`
- 쿠키 인증: `get_current_user` 의존성

## Dependencies
### External
- FastAPI, Uvicorn
- Tortoise-ORM, Aerich
- Pydantic V2
- python-jose (JWT)
- httpx (Cognito API)

<!-- MANUAL: -->
