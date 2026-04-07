# SSOS 도메인 주의사항 레퍼런스

ssos 프로젝트에서 반복적으로 발생한 버그와 주의사항 모음. 에이전트 작업 전 반드시 확인할 것.

## 1. 타임존 (최다 발생 버그)

**규칙**: 모든 datetime은 UTC로 저장, KST로 응답

```python
# backend/app/core/timezone.py 사용 필수
from app.core.timezone import KST, to_utc, to_kst

# 저장 시: KST → UTC
start_kst = datetime.combine(date, start_time, tzinfo=KST)
start_utc = to_utc(start_kst)
await Session.create(start_datetime=start_utc)

# 조회 시: UTC → KST
return {"date": to_kst(session.start_datetime).isoformat()}
```

**Session 모델 주의**:
- `start_datetime`, `end_datetime`: 실제 DB 필드 (UTC)
- `date`, `start_time`, `end_time`: KST 변환 프로퍼티 (읽기 전용)

## 2. 프론트엔드 날짜 직렬화

```javascript
// ❌ 금지 - UTC로 변환되어 KST 날짜가 하루 밀림
date.toISOString().split('T')[0]

// ✅ 올바른 방법
const y = date.getFullYear()
const m = String(date.getMonth() + 1).padStart(2, '0')
const d = String(date.getDate()).padStart(2, '0')
return `${y}-${m}-${d}`
```

## 3. Aerich 마이그레이션 파일명

형식: `NNNN_YYYYMMDDHHMMSS_description.py` (N은 반드시 **4자리**)

```
✅ 0005_20260131194857_add_memo_field.py
❌ 5_20260131_add_memo_field.py  (prefix가 4자리가 아님)
```

Aerich 자동 생성 후 파일명 반드시 확인. 필요 시 수동으로 4자리로 수정.

## 4. 테넌트 격리

모든 club 관련 쿼리에 `club_id` 필터 필수:

```python
# ✅ 올바른 방법
sessions = await Session.filter(club_id=club_id, ...)

# ❌ 위험 - 다른 동호회 데이터 노출 가능
sessions = await Session.filter(...)
```

## 5. Tortoise-ORM async 필수

```python
# 모든 DB 작업에 await 필수
count = await Match.filter(...).count()       # count도 await
exists = await Club.filter(...).exists()      # exists도 await
club = await Club.get(id=club_id)             # get도 await
```

## 6. CORS & 쿠키 인증

- 프론트엔드 모든 Axios 요청: `withCredentials: true`
- 백엔드 CORS: `allow_credentials=True`, origins에 프론트엔드 URL 포함
- Vite가 5173으로 폴백 시 `config.py`의 CORS_ORIGINS 업데이트 필요

## 7. Pydantic V2

```python
# ✅ V2 방식
class MySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

# ❌ V1 방식 (사용 불가)
class Config:
    orm_mode = True
```

## 8. Vue Router 순서

정적 경로가 동적 경로보다 먼저 정의되어야 함:

```javascript
// ✅ 올바른 순서
{ path: '/clubs/create', component: CreateClub },
{ path: '/clubs/:id', component: ClubDetail },

// ❌ 잘못된 순서 - 'create'가 :id로 매칭됨
{ path: '/clubs/:id', component: ClubDetail },
{ path: '/clubs/create', component: CreateClub },
```

## 9. 매칭 서비스 (sessions.py가 가장 복잡)

- `backend/app/api/sessions.py` (1,507줄): 세션 CRUD + 매칭 생성 모두 포함
- `matching_service.py`: 기본 알고리즘 (성별 그룹핑 → 랜덤 셔플 → 코트 배정)
- `ai_matching_service.py`: Google Gemini 기반 AI 매칭
- 매칭 타입: `MENS_DOUBLES`, `WOMENS_DOUBLES`, `MIXED_DOUBLES`, `SINGLES`

## 10. XSS 방지

```javascript
// v-html 사용 시 DOMPurify 필수
import DOMPurify from 'dompurify'
const safeHtml = DOMPurify.sanitize(userContent, { ALLOWED_TAGS: [] })
```

## 11. 소프트 딜리트 패턴

모든 모델이 `BaseModel`의 `is_deleted` 필드를 상속한다. 조회 쿼리에 반드시 `is_deleted=False` 필터를 포함할 것.

```python
# ✅ 올바른 방법
club = await Club.get_or_none(id=club_id, is_deleted=False)

# ❌ 위험 - 삭제된 데이터 노출 가능
club = await Club.get_or_none(id=club_id)
```

## 12. KSTDatetime 스키마 타입

Pydantic 스키마에 datetime 필드 추가 시 `KSTDatetime` 타입 사용으로 자동 UTC↔KST 변환:

```python
from app.core.timezone import KSTDatetime, OptionalKSTDatetime

class SessionCreate(BaseModel):
    start_datetime: KSTDatetime      # 필수
    end_datetime: OptionalKSTDatetime  # 선택
```

## 13. Enum/상수 동기화

백엔드 Enum과 프론트엔드 상수가 반드시 일치해야 한다:
- 백엔드: `models/*.py`의 Enum 정의
- 프론트엔드: `utils/constants.js`의 상수 정의
- 새 값 추가 시 양쪽 모두 업데이트 필수

## 14. 프론트엔드 유틸리티 사용 필수

- **날짜**: `src/utils/date.js` (dayjs 기반 `formatDate`, `formatDateTime` 등)
- **상수/라벨/색상**: `src/utils/constants.js` (하드코딩 금지)
- **API 클라이언트**: `src/api/index.js`의 apiClient만 사용 (별도 인스턴스 생성 금지)
