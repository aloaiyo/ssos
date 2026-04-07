<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-07 -->

# schemas

## Purpose
Pydantic V2 요청/응답 스키마. API의 입력 검증과 출력 직렬화를 담당한다.

## Key Files
| File | Description |
|------|-------------|
| `club.py` | Club 관련 스키마 |
| `event.py` | Event 스키마 |
| `match.py` | Match/MatchResult 스키마 |
| `member.py` | ClubMember 스키마 |
| `ranking.py` | Ranking 스키마 |
| `season.py` | Season 스키마 |
| `user.py` | User 프로필 스키마 |
| `schedule.py` | Schedule 스키마 |

## For AI Agents

### Working In This Directory
- Pydantic V2 필수: `model_config = ConfigDict(from_attributes=True)`
- ❌ `class Config: orm_mode = True` (V1 문법, 사용 금지)
- 프론트엔드가 필요로 하는 모든 필드를 응답 스키마에 포함
- datetime 필드는 KST 변환 후 반환

### Common Patterns
```python
from pydantic import BaseModel, ConfigDict

class ClubResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
```

<!-- MANUAL: -->
