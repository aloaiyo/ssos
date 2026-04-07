<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-07 -->

# api

## Purpose
Axios 기반 API 클라이언트 모듈. 백엔드 REST API와 통신하며, 쿠키 기반 인증을 자동 처리한다.

## Key Files
| File | Description |
|------|-------------|
| `index.js` | Axios 인스턴스 생성 (withCredentials, 인터셉터) |
| `auth.js` | Cognito 리다이렉트 URL, 인증 API |
| `clubs.js` | 동호회 API |
| `sessions.js` | 세션 API |
| `matches.js` | 경기 API |
| `members.js` | 회원 API |
| `rankings.js` | 랭킹 API |
| `seasons.js` | 시즌 API |
| `events.js` | 일정 API |
| `guests.js` | 게스트 API |
| `ocr.js` | OCR API |

## For AI Agents

### Working In This Directory
- `withCredentials: true` 반드시 유지 (쿠키 인증)
- 에러 핸들링: `error.response?.data?.detail || '기본 메시지'`
- 새 API 추가 시 `index.js`의 Axios 인스턴스 재사용
- baseURL은 `VITE_API_BASE_URL` 환경변수

<!-- MANUAL: -->
