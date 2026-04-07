<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-07 -->

# api

## Purpose
FastAPI 라우터 모듈. 각 도메인별 REST API 엔드포인트를 정의한다. `sessions.py`가 가장 복잡하며 매칭 생성 로직을 포함.

## Key Files
| File | Description |
|------|-------------|
| `sessions.py` | 세션 CRUD + 매칭 생성 (가장 복잡) |
| `matches.py` | 경기 결과 입력/조회 |
| `auth.py` | Cognito OAuth 콜백, 로그아웃, 현재 사용자 |
| `clubs.py` | 동호회 CRUD, 가입/탈퇴 |
| `members.py` | 회원 관리, 역할 변경 |
| `seasons.py` | 시즌 관리, 시즌별 랭킹 |
| `rankings.py` | 랭킹 조회/계산 |
| `events.py` | 일정 관리 |
| `fees.py` | 회비 관리 |
| `guests.py` | 게스트 참가자 관리 |
| `ocr.py` | 경기 결과 이미지 OCR 처리 |
| `announcements.py` | 공지사항 |
| `users.py` | 사용자 프로필 관리 |

## For AI Agents

### Working In This Directory
- 모든 club 관련 엔드포인트에 `club_id` 파라미터 필수
- 권한 체크: `require_club_member`, `require_club_manager` 의존성 사용
- 응답에 프론트엔드가 필요로 하는 모든 필드 포함 확인
- `error.response?.data?.detail` 패턴에 맞는 에러 응답 반환

### Common Patterns
```python
@router.get("/{club_id}/sessions")
async def list_sessions(club_id: int, member=Depends(require_club_member)):
    sessions = await Session.filter(event__club_id=club_id)
    ...
```

## Dependencies
### Internal
- `core/dependencies.py` — 인증/권한 의존성
- `services/` — 비즈니스 로직 위임
- `schemas/` — 요청/응답 직렬화
- `models/` — DB 접근

<!-- MANUAL: -->
