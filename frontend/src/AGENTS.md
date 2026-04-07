<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-07 -->

# src

## Purpose
프론트엔드 소스 코드 루트. Vue 3 앱의 모든 컴포넌트, 스토어, API 클라이언트, 라우터를 포함한다.

## Key Files
| File | Description |
|------|-------------|
| `App.vue` | 루트 컴포넌트 |
| `main.js` | Vue 앱 초기화, 플러그인 등록 |

## Subdirectories
| Directory | Purpose |
|-----------|---------|
| `views/` | 페이지 컴포넌트 (see `views/AGENTS.md`) |
| `components/` | 재사용 컴포넌트 (see `components/AGENTS.md`) |
| `stores/` | Pinia 상태 관리 (see `stores/AGENTS.md`) |
| `api/` | Axios API 클라이언트 (see `api/AGENTS.md`) |
| `router/` | Vue Router 설정 (see `router/AGENTS.md`) |
| `plugins/` | Vuetify 플러그인 설정 |
| `utils/` | 유틸리티 함수 (see `utils/AGENTS.md`) |
| `styles/` | 전역 CSS |

## For AI Agents

### Working In This Directory
- Composition API (`<script setup>`) 사용 필수
- 스토어를 통해 API 호출 (뷰에서 직접 API 호출 지양)
- `v-html` 사용 시 DOMPurify 필수

<!-- MANUAL: -->
