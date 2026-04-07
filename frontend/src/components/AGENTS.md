<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-07 -->

# components

## Purpose
재사용 가능한 Vue 컴포넌트. 레이아웃, 공통 UI, 경기 관련 컴포넌트로 분류된다.

## Subdirectories
| Directory | Purpose |
|-----------|---------|
| `layout/` | 앱 레이아웃 (AppBar, NavigationDrawer, Footer) |
| `common/` | 공통 컴포넌트 (ErrorAlert, LoadingSpinner, WeeklySchedulePicker) |
| `match/` | 경기 관련 (MatchCard, MatchSchedule) |

## For AI Agents

### Working In This Directory
- 새 공통 컴포넌트는 적절한 하위 디렉토리에 배치
- Vuetify 3 컴포넌트 활용 (자체 구현 최소화)
- Props는 명시적으로 정의

<!-- MANUAL: -->
