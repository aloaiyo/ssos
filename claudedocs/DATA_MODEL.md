# Data Model

## 개요

멀티테넌트 구조로, Club을 테넌트 경계로 사용합니다.
모든 club_id 필터링으로 테넌트 격리를 보장합니다.

---

## 엔티티 관계도

```
User (전역 사용자, cognito_sub linked)
  └── ClubMember (동호회 회원, role: manager/member/guest)
        └── Club (동호회) ← 테넌트 경계
              │
              ├── Season (시즌) ← 랭킹 집계 기간
              │     ├── Session (세션, Event 통해 연결)
              │     └── SeasonRanking (시즌별 랭킹)
              │
              ├── Event (일정)
              │     └── Session (세션)
              │           ├── SessionParticipant
              │           └── Match (경기)
              │                 ├── MatchParticipant
              │                 └── MatchResult
              │
              ├── Guest (게스트 참가자)
              ├── Announcement (공지사항)
              ├── FeeSetting (회비 정책)
              │     └── FeePayment (납부 기록)
              ├── ClubSchedule (정기 스케줄)
              └── Ranking (전체 랭킹, 시즌 독립)
```

---

## 핵심 모델

### User
```python
class User(BaseModel):
    email: str               # 유니크
    cognito_sub: str | None  # Cognito 사용자 ID
    name: str
    birth_date: date | None
    gender: Gender | None
    phone: str | None
    profile_image: str | None
    role: UserRole           # USER, SUPER_ADMIN
    subscription_tier: SubscriptionTier  # FREE, PREMIUM
```

### Club
```python
class Club(BaseModel):
    name: str
    description: str | None
    location: str | None
    default_num_courts: int = 2
    created_by: ForeignKey[User]
```

### ClubMember
```python
class ClubMember(BaseModel):
    club: ForeignKey[Club]
    user: ForeignKey[User]
    role: MemberRole         # MANAGER, MEMBER, GUEST
    status: MemberStatus     # PENDING, ACTIVE, INACTIVE, LEFT, BANNED
    gender: Gender           # MALE, FEMALE
    nickname: str
    skill_level: int | None  # 1-10
    join_date: date | None
```

---

## 시즌 관련

### Season
```python
class Season(BaseModel):
    club: ForeignKey[Club]
    name: str
    start_date: date
    end_date: date
    status: SeasonStatus     # UPCOMING, ACTIVE, COMPLETED
    description: str | None
```

### SeasonRanking
```python
class SeasonRanking(BaseModel):
    season: ForeignKey[Season]
    club_member: ForeignKey[ClubMember]
    points: int = 0          # 승3점/무1점/패0점
    rank: int | None
    wins: int = 0
    losses: int = 0
    draws: int = 0
    matches_played: int = 0
```

---

## 일정/세션 관련

### Event
```python
class Event(BaseModel):
    club: ForeignKey[Club]
    title: str
    event_type: EventType    # REGULAR, SPECIAL
    recurrence_rule: str | None  # RRULE 형식
    description: str | None
```

### Session
```python
class Session(BaseModel):
    event: ForeignKey[Event]
    season: ForeignKey[Season] | None
    date: date
    start_time: time
    end_time: time
    num_courts: int
    status: SessionStatus    # SCHEDULED, IN_PROGRESS, COMPLETED
    session_type: SessionType  # LEAGUE, TOURNAMENT
    notes: str | None
```

### SessionParticipant
```python
class SessionParticipant(BaseModel):
    session: ForeignKey[Session]

    # 3가지 참가자 유형 (하나만 설정)
    club_member: ForeignKey[ClubMember] | None   # MEMBER
    guest: ForeignKey[Guest] | None              # GUEST
    user: ForeignKey[User] | None                # ASSOCIATE

    category: ParticipantCategory   # MEMBER, GUEST, ASSOCIATE
    participation_type: ParticipationType  # MENS_DOUBLES, MIXED_DOUBLES, SINGLES
```

---

## 경기 관련

### Match
```python
class Match(BaseModel):
    session: ForeignKey[Session]
    match_type: MatchType    # MENS_DOUBLES, MIXED_DOUBLES, SINGLES
    court: int
    scheduled_time: time
    status: MatchStatus      # SCHEDULED, IN_PROGRESS, COMPLETED
    round_number: int | None
```

### MatchParticipant
```python
class MatchParticipant(BaseModel):
    match: ForeignKey[Match]

    # 3가지 참가자 유형 (하나만 설정)
    club_member: ForeignKey[ClubMember] | None
    guest: ForeignKey[Guest] | None
    user: ForeignKey[User] | None

    category: ParticipantCategory
    team: Team               # A, B
    position: int            # 1, 2 (복식에서의 순서)
```

### MatchResult
```python
class MatchResult(BaseModel):
    match: OneToOneField[Match]
    team_a_score: int
    team_b_score: int
    winner_team: Team | None  # A, B, None (무승부)
```

---

## 보조 모델

### Guest
```python
class Guest(BaseModel):
    club: ForeignKey[Club]
    name: str
    gender: Gender
    phone: str | None
    linked_member: ForeignKey[ClubMember] | None  # 나중에 회원 연결
```

### Ranking (시즌 독립)
```python
class Ranking(BaseModel):
    club: ForeignKey[Club]
    club_member: ForeignKey[ClubMember]
    points: int = 0
    rank: int | None
    wins: int = 0
    losses: int = 0
    draws: int = 0
    matches_played: int = 0
```

### Announcement
```python
class Announcement(BaseModel):
    club: ForeignKey[Club]
    author: ForeignKey[ClubMember]
    title: str
    content: str
    announcement_type: AnnouncementType  # GENERAL, IMPORTANT, EVENT
    is_pinned: bool = False
    views: int = 0
```

### FeeSetting
```python
class FeeSetting(BaseModel):
    club: ForeignKey[Club]
    name: str
    fee_type: FeeType        # MONTHLY, YEARLY, SESSION, ONE_TIME
    amount: int
    due_day: int | None      # 매월 몇 일
    description: str | None
    is_active: bool = True
```

### FeePayment
```python
class FeePayment(BaseModel):
    fee_setting: ForeignKey[FeeSetting]
    club_member: ForeignKey[ClubMember]
    target_year: int
    target_month: int | None
    amount_paid: int
    status: PaymentStatus    # PENDING, PAID, PARTIAL, EXEMPT
    paid_at: datetime | None
    notes: str | None
```

### ClubSchedule
```python
class ClubSchedule(BaseModel):
    club: ForeignKey[Club]
    day_of_week: int         # 0-6 (월-일)
    start_time: time
    end_time: time
    description: str | None
```

---

## Enum 정의

### 사용자
```python
class UserRole(str, Enum):
    USER = "user"
    SUPER_ADMIN = "super_admin"

class SubscriptionTier(str, Enum):
    FREE = "free"      # 1개 클럽 관리
    PREMIUM = "premium"  # 10개 클럽 관리
```

### 회원
```python
class MemberRole(str, Enum):
    MANAGER = "manager"
    MEMBER = "member"
    GUEST = "guest"

class MemberStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"
    LEFT = "left"
    BANNED = "banned"

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
```

### 경기
```python
class MatchType(str, Enum):
    MENS_DOUBLES = "mens_doubles"      # 남복: 4명 2v2
    WOMENS_DOUBLES = "womens_doubles"  # 여복: 4명 2v2
    MIXED_DOUBLES = "mixed_doubles"    # 혼복: 남녀 페어링
    SINGLES = "singles"                # 단식: 2명 1v1

class MatchStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class Team(str, Enum):
    A = "A"
    B = "B"
```

### 참가자
```python
class ParticipantCategory(str, Enum):
    MEMBER = "member"       # 정회원 (club_member)
    GUEST = "guest"         # 미가입 외부인 (guest)
    ASSOCIATE = "associate" # 준회원 (user)

class ParticipationType(str, Enum):
    MENS_DOUBLES = "mens_doubles"
    MIXED_DOUBLES = "mixed_doubles"
    SINGLES = "singles"
```

### 시즌
```python
class SeasonStatus(str, Enum):
    UPCOMING = "upcoming"
    ACTIVE = "active"
    COMPLETED = "completed"
```

### 기타
```python
class EventType(str, Enum):
    REGULAR = "regular"
    SPECIAL = "special"

class SessionType(str, Enum):
    LEAGUE = "league"
    TOURNAMENT = "tournament"

class SessionStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class AnnouncementType(str, Enum):
    GENERAL = "general"
    IMPORTANT = "important"
    EVENT = "event"

class FeeType(str, Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"
    SESSION = "session"
    ONE_TIME = "one_time"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    PARTIAL = "partial"
    EXEMPT = "exempt"
```

---

## 주요 관계

### 1:N 관계
- User → ClubMember (사용자는 여러 동호회 가입 가능)
- Club → ClubMember (동호회는 여러 회원 보유)
- Club → Season (동호회는 여러 시즌 보유)
- Season → SeasonRanking (시즌별 여러 랭킹)
- Session → SessionParticipant (세션에 여러 참가자)
- Session → Match (세션에 여러 경기)
- Match → MatchParticipant (경기에 여러 참가자)

### 1:1 관계
- Match → MatchResult (경기당 하나의 결과)

### 선택적 관계
- Guest ↔ ClubMember (게스트가 회원이 되면 연결)
- SessionParticipant → ClubMember | Guest | User (3가지 중 하나)
- MatchParticipant → ClubMember | Guest | User (3가지 중 하나)

---

## Soft Delete

모든 모델은 `is_deleted` 필드를 가지며, 실제 삭제 대신 논리적 삭제를 사용합니다.

```python
# 조회 시 항상 필터링
members = await ClubMember.filter(club_id=club_id, is_deleted=False)
```

---

*Last Updated: 2026-01-19*
