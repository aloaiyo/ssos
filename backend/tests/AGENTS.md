<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-07 -->

# tests

## Purpose
pytest 기반 백엔드 테스트. 매칭 알고리즘, 모델, 스키마, 보안, 타임존 테스트를 포함한다.

## Key Files
| File | Description |
|------|-------------|
| `conftest.py` | pytest 픽스처 (DB 설정, 테스트 데이터) |
| `test_matching_service.py` | 매칭 알고리즘 테스트 (가장 중요) |
| `test_models.py` | ORM 모델 테스트 |
| `test_schemas.py` | Pydantic 스키마 테스트 |
| `test_security.py` | JWT/인증 테스트 |
| `test_timezone.py` | 타임존 변환 테스트 |

## For AI Agents

### Working In This Directory
- 매칭 로직 변경 시 `test_matching_service.py` 반드시 실행
- `poetry run pytest -v` 로 상세 출력 확인

<!-- MANUAL: -->
