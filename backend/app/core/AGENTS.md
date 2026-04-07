<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-07 -->

# core

## Purpose
인증, 보안, 타임존 등 횡단 관심사(cross-cutting concerns) 모듈. JWT 토큰 처리, 쿠키 기반 인증 의존성, KST/UTC 변환 유틸리티.

## Key Files
| File | Description |
|------|-------------|
| `dependencies.py` | FastAPI 의존성 주입 (쿠키 인증, 권한 체크) |
| `security.py` | JWT 토큰 생성/검증 |
| `timezone.py` | KST 타임존 상수, `to_utc()`, `to_kst()` 변환 함수 |

## For AI Agents

### Working In This Directory
- `dependencies.py`의 의존성 체인 이해 필수:
  - `get_current_user` → `get_current_active_user` → `require_club_member` → `require_club_manager`
- 타임존 변환은 반드시 `timezone.py`의 함수 사용 (직접 변환 금지)
- JWT 시크릿은 환경변수 `SECRET_KEY`에서 로드

### Common Patterns
```python
from app.core.dependencies import require_club_member
from app.core.timezone import KST, to_utc, to_kst
```

<!-- MANUAL: -->
