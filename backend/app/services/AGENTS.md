<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-07 -->

# services

## Purpose
비즈니스 로직 서비스 계층. API 라우터에서 위임받은 복잡한 로직을 처리한다. 매칭 알고리즘이 핵심.

## Key Files
| File | Description |
|------|-------------|
| `matching_service.py` | 기본 매칭 알고리즘 — 참가자 그룹핑, 코트 배정, 시간 스케줄링 |
| `ai_matching_service.py` | AI 기반 매칭 (Google Gemini API 활용) |
| `auth_service.py` | Cognito 토큰 교환, 사용자 동기화, JWT 발급 |
| `cognito_service.py` | AWS Cognito API 래퍼 |
| `ocr_service.py` | 경기 결과 이미지 OCR (Google Gemini API) |

## For AI Agents

### Working In This Directory
- `matching_service.py` 수정 시 `test_matching_service.py` 테스트 필수 실행
- 매칭 타입: MENS_DOUBLES(남4), WOMENS_DOUBLES(여4), MIXED_DOUBLES(남2+여2), SINGLES(2)
- 혼복은 성별 페어링 로직 필수 (1남+1여 vs 1남+1여)
- OCR 서비스는 120초 타임아웃 설정

### Common Patterns
- 서비스 함수는 async, 트랜잭션 필요 시 `in_transaction()` 사용
- 외부 API 호출은 httpx 비동기 클라이언트 사용

## Dependencies
### Internal
- `models/` — DB 모델 접근
- `core/timezone.py` — 시간 변환
### External
- Google Gemini API (AI 매칭, OCR)
- AWS Cognito (인증)

<!-- MANUAL: -->
