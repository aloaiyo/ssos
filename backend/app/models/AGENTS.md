<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-07 -->

# models

## Purpose
Tortoise-ORM 데이터 모델. 멀티 테넌트(Club 기준) 구조이며, User → ClubMember → Club 관계가 핵심.

## Key Files
| File | Description |
|------|-------------|
| `base.py` | 공통 베이스 모델 (TimestampMixin 등) |
| `user.py` | User 모델 (cognito_sub 연동, 전역 사용자) |
| `club.py` | Club 모델 (테넌트 격리 단위) |
| `member.py` | ClubMember 모델 (역할: manager/member) |
| `event.py` | Event 모델 (일정) |
| `season.py` | Season + SeasonRanking 모델 |
| `match.py` | Match, MatchParticipant, MatchResult 모델 |
| `ranking.py` | 랭킹 관련 모델 |
| `guest.py` | Guest 모델 (비회원 참가자) |
| `fee.py` | Fee 모델 (회비) |
| `announcement.py` | Announcement 모델 (공지사항) |
| `schedule.py` | Schedule 모델 (정기 일정) |

## For AI Agents

### Working In This Directory
- 모델 변경 후 반드시 Aerich 마이그레이션 생성
- 마이그레이션 파일명: 4자리 prefix 확인 (예: `0005_...`)
- 모든 club 관련 모델은 `club_id` FK 포함 확인
- `__init__.py`에 새 모델 import 추가 필수 (Tortoise 모델 발견용)

### Data Model Hierarchy
```
User (전역)
  └── ClubMember (club_id FK)
        └── Club ← 테넌트 경계
              ├── Season → SeasonRanking
              ├── Event → Session → Match → MatchParticipant → MatchResult
              ├── Guest, Announcement, Fee
```

### Common Patterns
```python
class MyModel(TimestampMixin, Model):
    club = fields.ForeignKeyField("models.Club", related_name="my_models")
    class Meta:
        table = "my_models"
```

<!-- MANUAL: -->
