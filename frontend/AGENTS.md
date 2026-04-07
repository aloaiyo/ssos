<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-07 -->

# Frontend

## Purpose
Vue 3 + Vuetify 3 SPA. 동호회 관리 UI를 제공하며, Pinia 스토어로 상태 관리, Axios로 백엔드 API 통신. AWS Cognito OAuth 리다이렉트 인증 처리.

## Key Files
| File | Description |
|------|-------------|
| `package.json` | npm 의존성 및 스크립트 |
| `vite.config.js` | Vite 빌드 설정 (프로덕션에서 console.log 제거) |
| `eslint.config.js` | ESLint 9 flat config |
| `index.html` | SPA 진입점 |

## Subdirectories
| Directory | Purpose |
|-----------|---------|
| `src/` | 소스 코드 (see `src/AGENTS.md`) |
| `public/` | 정적 파일 |

## For AI Agents

### Working In This Directory
- `npm install` → `npm run dev` (포트 3000, 점유 시 5173)
- ESLint 9 flat config 사용 (`.eslintrc` 아님)
- 타임존 주의: `toISOString()` 대신 로컬 날짜 컴포넌트 사용
- XSS: `v-html` 사용 시 DOMPurify 필수

### Testing Requirements
```bash
npm run lint      # ESLint 검사
npm run lint:fix  # 자동 수정
npm run build     # 프로덕션 빌드 검증
```

### Common Patterns
- Vue 3 Composition API (`<script setup>`)
- Pinia 스토어 → API 호출 (직접 API 호출 지양)
- `withCredentials: true` (쿠키 인증)
- Vuetify 3 컴포넌트 (v-card, v-data-table 등)

## Dependencies
### External
- Vue 3, Vue Router
- Vuetify 3
- Pinia
- Axios
- DOMPurify

<!-- MANUAL: -->
