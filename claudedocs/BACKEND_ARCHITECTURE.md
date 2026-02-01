# Backend Architecture

## 개요

FastAPI 기반 비동기 백엔드로, Tortoise-ORM과 PostgreSQL을 사용합니다.

## 디렉토리 구조

```
backend/app/
├── main.py                  # FastAPI 앱 엔트리포인트
├── config.py                # 설정 관리 (Pydantic BaseSettings + AWS SSM)
├── models/                  # Tortoise-ORM 데이터베이스 모델 (13개)
├── schemas/                 # Pydantic V2 요청/응답 스키마 (9개)
├── api/                     # FastAPI 라우터 (14개)
├── services/                # 비즈니스 로직 서비스 (5개)
└── core/                    # 보안 및 의존성 주입
```

---

## 모델 계층

### 기본 모델 (`base.py`)
모든 모델의 기본 클래스로 Soft delete를 지원합니다.

```python
class BaseModel(Model):
    created_at: datetime
    modified_at: datetime
    is_deleted: bool = False
```

### 핵심 엔티티

| 모델 | 파일 | 역할 |
|------|------|------|
| User | user.py | 글로벌 사용자 (Cognito 연동) |
| Club | club.py | 테니스 동호회 (테넌트 단위) |
| ClubMember | member.py | 동호회 회원 (role: manager/member/guest) |
| Season | season.py | 순위 집계 기간 |
| SeasonRanking | season.py | 시즌별 개별 랭킹 |
| Event | event.py | 일정 (regular/special) |
| Session | event.py | 세션/경기 일정 |
| SessionParticipant | event.py | 세션 참가자 |
| Match | match.py | 개별 경기 |
| MatchParticipant | match.py | 경기 참가자 (Team A/B) |
| MatchResult | match.py | 경기 결과 |
| Ranking | ranking.py | 클럽 전체 랭킹 (시즌 독립) |
| Guest | guest.py | 미가입 게스트 |
| Announcement | announcement.py | 클럽 공지사항 |
| FeeSetting, FeePayment | fee.py | 회비 정책 및 납부 |
| ClubSchedule | schedule.py | 정기 활동 스케줄 |

### 주요 Enum

```python
# 사용자
UserRole: USER, SUPER_ADMIN
SubscriptionTier: FREE (1개), PREMIUM (10개 클럽)

# 회원
MemberRole: MANAGER, MEMBER, GUEST
MemberStatus: PENDING, ACTIVE, INACTIVE, LEFT, BANNED
Gender: MALE, FEMALE

# 경기
MatchType: MENS_DOUBLES, MIXED_DOUBLES, SINGLES, WOMENS_DOUBLES
MatchStatus: SCHEDULED, IN_PROGRESS, COMPLETED

# 시즌
SeasonStatus: UPCOMING, ACTIVE, COMPLETED

# 참가자
ParticipantCategory: MEMBER (정회원), GUEST (미가입), ASSOCIATE (준회원)
ParticipationType: MENS_DOUBLES, MIXED_DOUBLES, SINGLES
```

---

## 서비스 계층

### auth_service.py
Cognito 인증 코드를 로컬 사용자로 동기화합니다.

```python
async def sync_user_from_cognito_code(code: str) -> User:
    # 1. Cognito Authorization Code → ID Token 교환
    # 2. ID Token 검증 및 클레임 추출
    # 3. 로컬 DB 사용자 생성/업데이트
    # 4. 기존 이메일 사용자 마이그레이션
```

### cognito_service.py
AWS Cognito API 래퍼입니다.

```python
class CognitoService:
    @staticmethod
    def sign_up(email, password, name)      # 회원가입
    def confirm_sign_up(email, code)        # 이메일 인증
    def admin_initiate_auth(email, password) # 로그인
    def exchange_code_for_token(code)       # OAuth 코드 교환
    def verify_id_token(token)              # 토큰 검증
```

### matching_service.py
핵심 자동 매칭 알고리즘입니다.

```python
async def create_matches_for_session(session_id, ...) -> List[Match]:
    # 1. 참가자를 경기 타입별로 분류
    # 2. 랜덤 셔플로 공정한 팀 구성
    # 3. 코트/시간대 자동 배정

# 남복 (MENS_DOUBLES): 4명씩 2v2
# 여복 (WOMENS_DOUBLES): 4명씩 2v2
# 혼복 (MIXED_DOUBLES): 남녀 페어링 보장 (각 팀 남1, 여1)
# 단식 (SINGLES): 2명씩 1v1
```

### ai_matching_service.py
AI 기반 지능형 매칭 알고리즘입니다.

```python
async def generate_ai_matches(session_id, mode="balanced") -> List[Match]:
    # balanced: 실력 균형 고려
    # random: 완전 랜덤
    # 미리보기 생성 후 확정 가능
```

### ocr_service.py
테니스 경기 결과 이미지 처리 서비스입니다.

```python
async def extract_scores_from_image(image) -> OCRResult:
    # Google Gemini API로 이미지 OCR
    # 점수 파싱 및 검증
```

---

## 보안 계층

### security.py

```python
# 비밀번호
verify_password(plain, hash) -> bool
get_password_hash(password) -> str

# JWT 토큰 (HTTP-only 쿠키 저장)
create_access_token(user_id)   # 만료: 30일
create_refresh_token(user_id)  # 만료: 365일
verify_access_token(token) -> int | None  # user_id 반환
```

### dependencies.py

```python
# 인증 의존성
get_current_user(request) -> User          # 쿠키에서 토큰 검증
get_current_active_user(current_user)      # 활성 사용자 확인
require_super_admin(current_user)          # 슈퍼 관리자만

# 클럽 권한
class ClubPermission:
    def __init__(require_manager, exclude_guest, allow_inactive)
    def __call__(club_id, current_user) -> ClubMember

# 편의 별칭
require_club_member = ClubPermission()
require_club_manager = ClubPermission(require_manager=True)
require_club_member_not_guest = ClubPermission(exclude_guest=True)
```

---

## 설정 관리

### config.py

```python
class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str

    # JWT
    ACCESS_TOKEN_EXPIRE_DAYS: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 365

    # 쿠키
    COOKIE_SECURE: bool = False  # 프로덕션에서 True
    COOKIE_SAMESITE: str = "lax"

    # AWS Cognito
    COGNITO_USER_POOL_ID: str
    COGNITO_CLIENT_ID: str
    COGNITO_CLIENT_SECRET: str
    COGNITO_DOMAIN: str
    COGNITO_REDIRECT_URI: str

    # AWS SSM (프로덕션)
    USE_AWS_SSM: bool = False
    SSM_PREFIX: str = "/tennis-club/prod"
```

---

## 주요 패턴

### Timezone 처리 (UTC 저장, KST 응답)
```python
from app.core.timezone import KST, to_utc, to_kst

# 저장 시: KST → UTC 변환
start_kst = datetime.combine(date, start_time, tzinfo=KST)
start_datetime_utc = to_utc(start_kst)
await Session.create(start_datetime=start_datetime_utc, ...)

# 조회 시: UTC → KST 변환
return {"date": session.date.isoformat()}  # 프로퍼티가 자동 변환
```

**Session 모델**:
- 저장 필드: `start_datetime`, `end_datetime` (UTC)
- KST 프로퍼티: `date`, `start_time`, `end_time` (자동 변환)

### Soft Delete
```python
# 모든 쿼리에서 is_deleted=False 필터 적용
members = await ClubMember.filter(club_id=club_id, is_deleted=False)
```

### Pydantic V2
```python
class ClubSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # NOT orm_mode
```

### 비동기 처리
```python
# 모든 DB 작업에 await 필수
count = await Match.filter(session_id=session_id).count()  # .count()도 await
exists = await User.filter(email=email).exists()           # .exists()도 await
```

### 트랜잭션
```python
from tortoise.transactions import in_transaction

async with in_transaction():
    match = await Match.create(...)
    await MatchParticipant.create(match=match, ...)
```

### 다중 참가자 카테고리
```python
# SessionParticipant / MatchParticipant
# - MEMBER: club_member 설정 (정회원)
# - GUEST: guest 설정 (미가입 외부인)
# - ASSOCIATE: user 설정 (시스템 가입, 동호회 미가입)

def get_participant_name(self):
    if self.category == ParticipantCategory.MEMBER:
        return self.club_member.nickname
    elif self.category == ParticipantCategory.GUEST:
        return self.guest.name
    else:
        return self.user.name
```

---

## API 응답 패턴

### 성공
```json
{
  "id": 1,
  "name": "동호회명",
  "created_at": "2025-01-15T10:00:00"
}
```

### 에러
```json
{
  "detail": "에러 메시지"
}
```

### 상태 코드
- 200: OK
- 201: Created
- 204: No Content (삭제)
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found

---

*Last Updated: 2026-02-01*
