<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-07 -->

# migrations

## Purpose
Aerich DB 마이그레이션 파일. Tortoise-ORM 모델 변경을 추적하고 DB 스키마를 업데이트한다.

## Subdirectories
| Directory | Purpose |
|-----------|---------|
| `models/` | 마이그레이션 파일들 |

## For AI Agents

### Working In This Directory
- 마이그레이션 파일명 규칙: `NNNN_YYYYMMDDHHMMSS_description.py` (4자리 prefix 필수)
- ❌ `5_20260131_...` → ✅ `0005_20260131_...`
- 자동 생성 후 prefix 확인 필요
- 순서: `aerich migrate --name "설명"` → `aerich upgrade`
- 롤백: `aerich downgrade`

<!-- MANUAL: -->
