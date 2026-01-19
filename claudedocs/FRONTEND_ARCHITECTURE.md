# Frontend Architecture

## 개요

Vue 3 Composition API 기반 SPA로, Vuetify 3 UI와 Pinia 상태 관리를 사용합니다.

## 디렉토리 구조

```
frontend/src/
├── views/              # 페이지 컴포넌트 (31개)
├── components/         # 재사용 컴포넌트 (8개)
├── stores/             # Pinia 스토어 (7개)
├── api/                # API 클라이언트 (12개)
├── router/             # Vue Router (42개 라우트)
├── utils/              # 유틸리티 함수 (date.js, validators.js)
├── plugins/            # Vuetify 설정
├── styles/             # 글로벌 CSS
├── App.vue             # 루트 컴포넌트
└── main.js             # 엔트리 포인트
```

---

## 라우팅

### 주요 라우트

| 경로 | 컴포넌트 | 인증 |
|------|---------|------|
| `/` | LandingView | 비로그인만 |
| `/dashboard` | HomeView | 필수 |
| `/auth/login` | LoginView | 게스트만 |
| `/auth/register` | RegisterView | 게스트만 |
| `/auth/callback` | CallbackView | OAuth |
| `/clubs` | ClubListView | 필수 |
| `/clubs/:id` | ClubDetailView | 필수 |
| `/clubs/:id/manage` | ClubManageView | 필수 |
| `/members` | MemberListView | 필수 |
| `/seasons` | SeasonListView | 필수 |
| `/seasons/:seasonId` | SeasonDetailView | 필수 |
| `/sessions` | SessionListView | 필수 |
| `/matches` | MatchScheduleView | 필수 |
| `/rankings` | RankingView | 필수 |

### 네비게이션 가드

```javascript
// router/index.js
router.beforeEach(async (to, from, next) => {
  // 1. 인증 상태 확인 (쿠키 기반)
  // 2. 프로필 완성 여부 체크 (gender, birth_date)
  // 3. 미완성 시 /auth/complete-profile로 리다이렉트
})
```

---

## Pinia 스토어

### auth.js - 인증 스토어

**상태:**
```javascript
{
  user: null,           // 현재 사용자
  isAuthenticated: false,
  isLoading: false,
  error: null,
  pendingEmail: null    // 이메일 인증 대기
}
```

**계산 속성:**
- `isAdmin` - super_admin 역할
- `isPremium` - 프리미엄 사용자
- `isProfileComplete` - 프로필 완성 여부

**주요 액션:**
- `register(email, password, name)` - 회원가입
- `verifyEmail(email, code)` - 이메일 인증
- `login(email, password)` - 로그인
- `logout()` - 로그아웃
- `checkAuth()` - 인증 상태 확인
- `handleCallback(code)` - OAuth 콜백

### club.js - 동호회 스토어

**상태:**
```javascript
{
  clubs: [],            // 내 동호회 목록
  currentClub: null,    // 현재 동호회 상세
  selectedClubId: null, // 선택된 동호회 (localStorage)
  isAdminMode: false    // 관리자 모드 (localStorage)
}
```

**계산 속성:**
- `selectedClub` - 선택된 동호회 정보
- `isManagerOfSelectedClub` - 매니저 여부

**주요 액션:**
- `fetchClubs()` - 내 동호회 목록
- `searchClubs(search)` - 전체 검색
- `selectClub(clubId)` - 동호회 선택
- `toggleAdminMode()` - 관리자 모드 토글

### season.js - 시즌 스토어

**상태:**
```javascript
{
  seasons: [],
  currentSeason: null,
  seasonRankings: []
}
```

**계산 속성:**
- `activeSeasons` - 진행 중 시즌
- `upcomingSeasons` - 예정 시즌
- `completedSeasons` - 완료 시즌

### session.js - 세션 스토어 (279 lines)

**상태:**
```javascript
{
  sessions: [],
  currentSession: null,
  participants: [],
  expandedSessions: []
}
```

**주요 액션:**
- `fetchSessions(clubId)` - 세션 목록 조회
- `createSession(clubId, sessionData)` - 세션 생성
- `addParticipant(clubId, sessionId, data)` - 참가자 추가
- `removeParticipant(clubId, sessionId, participantId)` - 참가자 제거

### match.js - 경기 스토어 (168 lines)

**상태:**
```javascript
{
  matches: [],
  currentMatch: null,
  isLoading: false,
  error: null
}
```

**주요 액션:**
- `generateMatches(clubId, sessionId, config)` - 경기 자동 생성
- `fetchMatches(clubId, sessionId)` - 경기 목록 조회
- `updateMatch(clubId, matchId, data)` - 경기 수정
- `recordResult(clubId, matchId, resultData)` - 결과 기록
- `deleteMatch(clubId, matchId)` - 경기 삭제

### ranking.js - 랭킹 스토어 (94 lines)

**상태:**
```javascript
{
  rankings: [],
  isLoading: false,
  error: null
}
```

**주요 액션:**
- `fetchRankings(clubId)` - 랭킹 목록 조회
- `fetchMemberRanking(clubId, memberId)` - 회원별 랭킹 조회
- `updateRankings(clubId)` - 랭킹 업데이트

### member.js - 회원 스토어 (148 lines)

기본 CRUD 상태 관리 (회원 목록, 역할 변경 등)

---

## API 클라이언트

### index.js - Axios 설정

```javascript
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 30000,
  withCredentials: true  // HTTP-only 쿠키 자동 전송
})

// 토큰 자동 갱신
api.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      // /auth/refresh로 토큰 갱신 시도
      // 갱신 실패 시 로그인 페이지로 리다이렉트
    }
  }
)
```

### auth.js

```javascript
getGoogleLoginUrl()      // Cognito Hosted UI URL
getCognitoLogoutUrl()    // 로그아웃 URL
register(email, password, name)
verifyEmail(email, code)
login(email, password)
logout()
refresh()
getCurrentUser()
handleCallback(code)
```

### clubs.js, members.js, seasons.js, sessions.js

표준 CRUD API 클라이언트

---

## 주요 페이지 컴포넌트

### HomeView.vue - 대시보드

**동호회 없음:**
- 온보딩 화면
- 동호회 생성/찾기 가이드

**동호회 있음:**
- Bento Grid 레이아웃
- 동호회 정보 카드 (Hero)
- 내 순위 카드 (Top 5)
- 다가오는 일정 (최대 3개)
- 빠른 액션 버튼
- Top 5 랭킹 카드

### ClubManageView.vue - 동호회 관리

6개 탭 구조:
1. ClubInfoTab - 기본 정보
2. MemberManagementTab - 회원 관리
3. SessionManagementTab - 세션 관리
4. AnnouncementTab - 공지사항
5. FeeManagementTab - 회비 관리
6. ClubStatsTab - 통계

### SeasonListView.vue - 시즌 목록

- 시즌 카드 리스트
- 상태별 필터링
- 생성/수정/삭제 다이얼로그

---

## 레이아웃 컴포넌트

### AppBar.vue

```
┌─────────────────────────────────────────────────────────┐
│ 메뉴  │  동호회 선택 드롭다운  │    알림  │  사용자 메뉴 │
└─────────────────────────────────────────────────────────┘
```

- 높이: 64px
- 동호회 선택 시 localStorage 저장
- 매니저 여부 표시

### NavigationDrawer.vue

```
┌──────────────────────┐
│     로고 / 동호회명   │
├──────────────────────┤
│ 홈                   │
│ 회원 목록            │
├──────────────────────┤
│ [일정 & 경기]        │
│  시즌               │
│  세션               │
│  경기 기록           │
│  랭킹               │
├──────────────────────┤
│ 설정                │
└──────────────────────┘
```

- 너비: 260px
- 반응형: 모바일(≤1024px) temporary, 데스크톱 permanent

---

## 데이터 흐름

```
사용자 상호작용
    ↓
View 컴포넌트 (emit/click)
    ↓
Store 액션 (비즈니스 로직)
    ↓
API 클라이언트 (HTTP 요청)
    ↓
Backend (응답)
    ↓
Store 상태 업데이트
    ↓
View 리렌더링 (반응형)
```

---

## 개발 패턴

### Composition API

```vue
<script setup>
import { ref, onMounted } from 'vue'
import { useClubStore } from '@/stores/club'

const clubStore = useClubStore()

onMounted(async () => {
  await clubStore.fetchClubs()
})
</script>
```

### Store 사용

```javascript
// 직접 API 호출 대신 Store 액션 사용
const clubStore = useClubStore()
await clubStore.fetchClubs()  // API 호출 + 상태 업데이트
```

### localStorage 동기화

```javascript
// club.js
watch(() => state.selectedClubId, (newId) => {
  localStorage.setItem('selectedClubId', newId)
})
```

---

## UI/UX 패턴

- Bento Grid 레이아웃 (반응형)
- Glass-morphism 디자인 (반투명 카드)
- Gradient 배경색
- Vuetify 3 컴포넌트
- 다크모드 지원 가능

---

## 개발 상태

**Phase 1 (완료):**
- 인증 UI (로그인, 회원가입, OAuth)
- 동호회 CRUD
- 회원 관리
- 기본 레이아웃

**Phase 2 (완료):**
- 시즌 관리 UI
- 세션 생성/참가자 관리
- 경기 자동 매칭 UI (기본 + AI)
- 결과 입력
- 랭킹 표시
- 코드 품질 개선 (ESLint, DOMPurify)

---

## 보안 패턴

### XSS 방지 (DOMPurify)
```javascript
import DOMPurify from 'dompurify'

function formatContent(content) {
  const sanitized = DOMPurify.sanitize(content, { ALLOWED_TAGS: [] })
  return sanitized.replace(/\n/g, '<br>')
}
```

### ESLint 설정
- ESLint 9 flat config 사용 (`eslint.config.js`)
- `no-console`: warn (프로덕션 빌드에서 자동 제거)
- `vue/no-v-html`: warn

### Production 빌드
```javascript
// vite.config.js
esbuild: {
  drop: process.env.NODE_ENV === 'production' ? ['console', 'debugger'] : []
}
```

---

## 의존성

### 핵심 프레임워크
- vue@3.4.21
- vue-router@4.3.0
- pinia@2.1.7
- vuetify@3.5.7

### HTTP & 데이터
- axios@1.6.7
- dayjs@1.11.10

### UI & 아이콘
- @mdi/font@7.4.47

### 유틸리티
- lodash@4.17.21
- dompurify@3.3.1

### 개발 도구
- vite@5.1.5
- eslint@9.39.2
- eslint-plugin-vue@10.7.0

---

*Last Updated: 2026-01-19*
