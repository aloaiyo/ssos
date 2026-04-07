<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-07 -->

# views

## Purpose
페이지 단위 Vue 컴포넌트. 각 도메인별 디렉토리로 구성되며, 라우터와 1:1 매핑된다.

## Key Files
| File | Description |
|------|-------------|
| `HomeView.vue` | 홈 페이지 (로그인 후 대시보드) |
| `LandingView.vue` | 랜딩 페이지 (비로그인 사용자) |
| `NotFoundView.vue` | 404 페이지 |

## Subdirectories
| Directory | Purpose |
|-----------|---------|
| `auth/` | 인증 관련 (로그인, 콜백, 회원가입, 프로필 완성) |
| `club/` | 동호회 (목록, 상세, 생성, 관리) + 하위 컴포넌트 |
| `session/` | 세션 (목록, 생성, 상세) |
| `match/` | 경기 (생성, 스케줄, 결과, 업로드) |
| `member/` | 회원 (목록, 관리) |
| `ranking/` | 랭킹 뷰 |
| `season/` | 시즌 (목록, 상세) |
| `profile/` | 내 프로필 |

## For AI Agents

### Working In This Directory
- 라우터 순서 주의: `/clubs/create`가 `/clubs/:id`보다 먼저 정의
- 신규 사용자는 프로필 완성 페이지로 리다이렉트됨
- 뷰에서 직접 API 호출 대신 Pinia 스토어 액션 사용

<!-- MANUAL: -->
