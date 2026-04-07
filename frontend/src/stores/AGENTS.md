<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-07 -->

# stores

## Purpose
Pinia 상태 관리 스토어. 각 도메인별 상태, API 호출, 캐싱을 담당한다.

## Key Files
| File | Description |
|------|-------------|
| `auth.js` | 인증 상태, 로그인/로그아웃, 현재 사용자 |
| `club.js` | 동호회 목록/상세, 가입/생성 |
| `session.js` | 세션 CRUD, 참가자 관리 |
| `match.js` | 경기 생성/결과, 매칭 알고리즘 호출 |
| `member.js` | 회원 목록, 역할 관리 |
| `ranking.js` | 랭킹 데이터 |
| `season.js` | 시즌 관리 |

## For AI Agents

### Working In This Directory
- 스토어 액션에서 API 호출, 뷰에서는 스토어 액션만 사용
- 에러 핸들링은 스토어에서 처리 후 상태로 노출
- `defineStore` 사용 (Options API 또는 Setup 문법)

<!-- MANUAL: -->
