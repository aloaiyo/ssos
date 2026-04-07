<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-07 -->

# router

## Purpose
Vue Router 설정. 라우트 정의, 인증 가드, 프로필 완성 체크, 관리자 권한 체크를 포함한다.

## Key Files
| File | Description |
|------|-------------|
| `index.js` | 전체 라우트 정의 및 네비게이션 가드 |

## For AI Agents

### Working In This Directory
- 라우트 순서 중요: 정적 경로(`/clubs/create`)가 동적 경로(`/clubs/:id`)보다 먼저
- 가드 순서: 인증 → 프로필 완성 → 관리자 권한
- 새 라우트 추가 시 적절한 meta 필드 설정 (`requiresAuth`, `requiresManager` 등)

<!-- MANUAL: -->
