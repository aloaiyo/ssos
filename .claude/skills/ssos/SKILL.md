---
name: ssos
description: "테니스 동호회 관리 시스템(ssos) 개발 오케스트레이터. 기능 추가, 버그 수정, API 변경, UI 개선 등 모든 개발 작업에서 backend-dev + frontend-dev + reviewer 에이전트 팀을 조율한다. '기능 추가해줘', '버그 수정해줘', 'API 만들어줘', '화면 만들어줘', '세션/매칭/OCR/랭킹/회비 관련 작업' 등 개발 요청이 오면 반드시 이 스킬을 사용할 것. '다시 실행', '재실행', '수정해줘', '보완해줘', '이전 작업 이어서' 같은 후속 요청에도 적용."
---

# SSOS 개발 오케스트레이터

테니스 동호회 관리 시스템의 개발 작업을 에이전트 팀으로 조율한다.

## 팀 구성

| 에이전트 | 역할 |
|---------|------|
| `backend-dev` | FastAPI/Tortoise-ORM 백엔드 구현 |
| `frontend-dev` | Vue 3/Vuetify 프론트엔드 구현 |
| `reviewer` | API↔Frontend 경계면 정합성 검증 |

## Phase 0: 컨텍스트 확인

워크플로우 시작 전 기존 산출물 유무를 확인한다:

- `_workspace/` 존재 + 부분 수정 요청 → **부분 재실행** (해당 에이전트만 재호출)
- `_workspace/` 존재 + 새 요청 → **새 실행** (`_workspace/`를 `_workspace_prev/`로 이동)
- `_workspace/` 미존재 → **초기 실행**

## Phase 1: 요청 분석 및 범위 결정

1. 요청 유형 판별:
   - **기능 개발**: 백엔드 + 프론트엔드 모두 필요 → Phase 2A
   - **백엔드 전용**: API/모델/서비스만 변경 → Phase 2B
   - **프론트엔드 전용**: UI/스토어만 변경 → Phase 2C
   - **버그 수정**: 원인 파악 → 영향 범위에 따라 2A/2B/2C

2. 복잡도 판별:
   - 간단 (단일 파일, 명확한 변경) → 에이전트 팀 없이 직접 처리
   - 복잡 (여러 파일, API 계약 변경 포함) → 에이전트 팀 조율

3. `_workspace/` 디렉토리 생성 (복잡도 높을 때)

## Phase 2A: 풀스택 기능 개발 (에이전트 팀)

```
TeamCreate → backend-dev + frontend-dev 병렬 실행 → reviewer 순차 실행
```

**팀 실행 순서:**

1. `backend-dev`에게 할당:
   - API 엔드포인트/스키마/서비스 구현
   - API 스펙을 `_workspace/api-contract.md`에 기록

2. `frontend-dev`에게 할당 (기존 API에 변경이 없으면 backend-dev와 병렬, API 변경 시 순차):
   - `_workspace/api-contract.md` 기준으로 UI/스토어 구현
   - backend-dev 완료 전이면 임시 mock 데이터로 개발 후 실제 연동

3. `reviewer`에게 할당 (backend-dev + frontend-dev 완료 후):
   - API 경계면 정합성 검증
   - 타임존/CORS/테넌트 격리 이슈 검사
   - 이슈 발견 시 해당 에이전트에 수정 요청

## Phase 2B: 백엔드 전용

`backend-dev` 단독 실행 → `reviewer`가 백엔드 내부 검증 (타임존, 테넌트 격리)

## Phase 2C: 프론트엔드 전용

`frontend-dev` 단독 실행 → `reviewer`가 타임존/XSS/에러 처리 패턴 검증

## Phase 3: 결과 종합 및 보고

1. 변경된 파일 목록 정리
2. **백엔드 변경 시 pytest 실행** (`poetry run pytest` — 최소한 관련 테스트)
3. **프론트엔드 변경 시 ESLint 실행** (`npm run lint`)
4. 마이그레이션 필요 여부 명시
5. 검증 결과 요약
6. 남은 이슈 또는 후속 작업 권장사항

## 데이터 전달 규칙

- 중간 산출물: `_workspace/` (파일명: `{phase}_{agent}_{artifact}.ext`)
- API 계약: `_workspace/api-contract.md`
- 최종 결과: 실제 소스 파일에 직접 반영

## 에러 핸들링

- 에이전트 실패 시: 1회 재시도, 재실패 시 결과 없이 진행 (보고서에 명시)
- API 계약 불일치: reviewer가 감지 → 해당 에이전트에 수정 요청 후 재검증

## ssos 도메인 주의사항

> 상세 내용은 `references/domain-gotchas.md` 참조

핵심만 요약:
- **타임존**: UTC 저장, KST 표시 — `app.core.timezone` 모듈 필수 사용
- **날짜 직렬화**: 프론트엔드에서 `toISOString()` 금지
- **테넌트 격리**: `club_id` 필터 필수
- **Aerich**: 마이그레이션 파일명 4자리 prefix 확인
- **인증**: `withCredentials: true`, HTTP-only 쿠키

## 테스트 시나리오

### 정상 흐름
- 요청: "세션에 참가자 메모 필드 추가해줘"
- Phase 1: 풀스택 기능 개발 판별
- Phase 2A: backend-dev(DB 모델+API) ‖ frontend-dev(UI+스토어) → reviewer(검증)
- Phase 3: 변경 파일 목록 + 마이그레이션 안내

### 에러 흐름
- reviewer가 타임존 버그 감지 → frontend-dev에 수정 요청 → 재검증
