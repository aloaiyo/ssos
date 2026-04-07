<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-07 -->

# utils

## Purpose
프론트엔드 유틸리티 함수 모음. 날짜 포맷팅, 상수 정의, 입력 검증을 제공한다.

## Key Files
| File | Description |
|------|-------------|
| `date.js` | 날짜 포맷팅 — KST 타임존 처리 주의 |
| `constants.js` | 앱 전역 상수 (매치 타입, 역할 등) |
| `validators.js` | 입력 검증 함수 |

## For AI Agents

### Working In This Directory
- ⚠️ `toISOString()` 사용 금지 — UTC 변환으로 날짜 밀림
- 로컬 날짜: `getFullYear()`, `getMonth()`, `getDate()` 사용
- 새 유틸리티 추가 시 기존 패턴 따르기

<!-- MANUAL: -->
