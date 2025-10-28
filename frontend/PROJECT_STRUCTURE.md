# 프로젝트 구조

```
frontend/
├── public/                          # 정적 파일
│   └── favicon.ico
│
├── src/
│   ├── main.js                      # Vue 앱 엔트리포인트
│   ├── App.vue                      # 루트 컴포넌트
│   │
│   ├── router/                      # Vue Router 설정
│   │   └── index.js                 # 라우트 정의 및 네비게이션 가드
│   │
│   ├── stores/                      # Pinia 스토어 (상태 관리)
│   │   ├── auth.js                  # 인증 (로그인, 회원가입, 사용자 정보)
│   │   ├── club.js                  # 동호회 (CRUD, 선택)
│   │   ├── member.js                # 회원 (CRUD, 통계)
│   │   ├── session.js               # 세션 (Phase 2)
│   │   ├── match.js                 # 매치 (Phase 2)
│   │   └── ranking.js               # 랭킹 (Phase 2)
│   │
│   ├── api/                         # API 클라이언트
│   │   ├── index.js                 # Axios 설정 및 인터셉터
│   │   ├── auth.js                  # 인증 API
│   │   ├── clubs.js                 # 동호회 API
│   │   ├── members.js               # 회원 API
│   │   ├── events.js                # 이벤트 API (Phase 2)
│   │   ├── sessions.js              # 세션 API (Phase 2)
│   │   ├── matches.js               # 매치 API (Phase 2)
│   │   └── rankings.js              # 랭킹 API (Phase 2)
│   │
│   ├── components/                  # 재사용 가능한 컴포넌트
│   │   ├── layout/                  # 레이아웃 컴포넌트
│   │   │   ├── AppBar.vue           # 상단 앱바 (로고, 동호회 선택, 사용자 메뉴)
│   │   │   ├── NavigationDrawer.vue # 사이드 네비게이션 드로어
│   │   │   └── Footer.vue           # 하단 푸터
│   │   │
│   │   ├── common/                  # 공통 컴포넌트
│   │   │   ├── LoadingSpinner.vue   # 전역 로딩 스피너
│   │   │   └── ErrorAlert.vue       # 전역 에러 알림
│   │   │
│   │   └── match/                   # 매치 관련 컴포넌트 (Phase 2)
│   │       ├── MatchCard.vue        # 매치 카드
│   │       └── MatchSchedule.vue    # 매치 스케줄
│   │
│   ├── views/                       # 페이지 컴포넌트
│   │   ├── HomeView.vue             # 홈 페이지 (대시보드)
│   │   ├── NotFoundView.vue         # 404 페이지
│   │   │
│   │   ├── auth/                    # 인증 페이지
│   │   │   ├── LoginView.vue        # 로그인
│   │   │   └── RegisterView.vue     # 회원가입
│   │   │
│   │   ├── club/                    # 동호회 페이지
│   │   │   ├── ClubListView.vue     # 동호회 목록 (카드 뷰)
│   │   │   ├── ClubDetailView.vue   # 동호회 상세 정보
│   │   │   └── ClubManageView.vue   # 동호회 관리 (생성/수정/삭제)
│   │   │
│   │   ├── member/                  # 회원 페이지
│   │   │   ├── MemberListView.vue   # 회원 목록 (테이블 뷰, 필터링)
│   │   │   └── MemberManageView.vue # 회원 관리 (추가/수정/삭제)
│   │   │
│   │   ├── session/                 # 세션 페이지 (Phase 2)
│   │   │   ├── SessionListView.vue
│   │   │   ├── SessionDetailView.vue
│   │   │   └── SessionCreateView.vue
│   │   │
│   │   ├── match/                   # 매치 페이지 (Phase 2)
│   │   │   ├── MatchGenerateView.vue
│   │   │   ├── MatchScheduleView.vue
│   │   │   └── MatchResultView.vue
│   │   │
│   │   └── ranking/                 # 랭킹 페이지 (Phase 2)
│   │       └── RankingView.vue
│   │
│   ├── plugins/                     # Vue 플러그인
│   │   └── vuetify.js               # Vuetify 설정 (테마, 디폴트)
│   │
│   ├── styles/                      # 전역 스타일
│   │   └── main.css                 # 전역 CSS
│   │
│   └── utils/                       # 유틸리티 함수
│       ├── date.js                  # 날짜 포맷팅 (Day.js)
│       └── validators.js            # 폼 유효성 검사
│
├── index.html                       # HTML 엔트리포인트
├── vite.config.js                   # Vite 설정
├── package.json                     # 프로젝트 의존성
├── .env                             # 환경 변수
├── .gitignore                       # Git 제외 파일
├── README.md                        # 프로젝트 소개
├── INSTALL.md                       # 설치 및 실행 가이드
└── PROJECT_STRUCTURE.md             # 이 파일

```

## 주요 기능별 파일 매핑

### 인증 (Authentication)
- **Store**: `stores/auth.js`
- **API**: `api/auth.js`
- **Views**: `views/auth/LoginView.vue`, `views/auth/RegisterView.vue`
- **기능**: 로그인, 회원가입, JWT 토큰 관리, 사용자 정보 로드

### 동호회 관리 (Club Management)
- **Store**: `stores/club.js`
- **API**: `api/clubs.js`
- **Views**:
  - `views/club/ClubListView.vue` - 목록 및 선택
  - `views/club/ClubDetailView.vue` - 상세 정보
  - `views/club/ClubManageView.vue` - CRUD 관리
- **기능**: 동호회 생성/수정/삭제, 동호회 선택 (localStorage)

### 회원 관리 (Member Management)
- **Store**: `stores/member.js`
- **API**: `api/members.js`
- **Views**:
  - `views/member/MemberListView.vue` - 목록 및 필터링
  - `views/member/MemberManageView.vue` - CRUD 관리
- **기능**: 회원 추가/수정/삭제, 성별/선호타입 관리

### 레이아웃 (Layout)
- **Components**:
  - `components/layout/AppBar.vue` - 상단바
  - `components/layout/NavigationDrawer.vue` - 사이드 메뉴
  - `components/layout/Footer.vue` - 하단바
- **기능**: 전역 네비게이션, 동호회 선택, 사용자 메뉴

### 공통 (Common)
- **Components**:
  - `components/common/LoadingSpinner.vue` - 로딩 UI
  - `components/common/ErrorAlert.vue` - 에러 알림
- **Utils**:
  - `utils/date.js` - 날짜 포맷팅
  - `utils/validators.js` - 폼 검증

## 라우트 구조

```
/                         → HomeView (대시보드)
/auth/login               → LoginView
/auth/register            → RegisterView
/clubs                    → ClubListView
/clubs/:id                → ClubDetailView
/clubs/manage             → ClubManageView (admin)
/members                  → MemberListView
/members/manage           → MemberManageView (admin)
```

## 네비게이션 가드

**인증 필요 (`requiresAuth`)**:
- 홈 페이지
- 동호회 관련 페이지
- 회원 관련 페이지

**게스트 전용 (`requiresGuest`)**:
- 로그인
- 회원가입

**관리자 전용 (`requiresAdmin`)**:
- 동호회 관리
- 회원 관리

## 상태 관리 (Pinia)

각 스토어는 다음 패턴을 따릅니다:

```javascript
// State
const items = ref([])
const currentItem = ref(null)
const isLoading = ref(false)
const error = ref(null)

// Getters (computed)
const selectedItem = computed(() => { ... })

// Actions
async function fetchItems() { ... }
async function createItem(data) { ... }
async function updateItem(id, data) { ... }
async function deleteItem(id) { ... }
```

## API 클라이언트

**Axios 인터셉터**:
- 요청: JWT 토큰 자동 추가
- 응답: 에러 처리 (401, 403, 500)

**Base URL**: `http://localhost:8000` (환경 변수)

## 스타일링

**Vuetify 3 테마**:
```javascript
{
  primary: '#1976D2',    // 블루
  secondary: '#424242',  // 다크 그레이
  accent: '#FF9800',     // 오렌지
  success: '#4CAF50',    // 그린
  warning: '#FFC107',    // 옐로우
  error: '#F44336',      // 레드
}
```

**반응형 브레이크포인트**:
- xs: < 600px (모바일)
- sm: 600px - 960px (태블릿)
- md: 960px - 1264px (데스크톱)
- lg: 1264px - 1904px (대형 데스크톱)
- xl: > 1904px (초대형)

## Phase 2 준비

Phase 2 기능을 위한 파일 구조는 이미 생성되어 있습니다:

- **Stores**: `session.js`, `match.js`, `ranking.js`
- **API**: `sessions.js`, `matches.js`, `rankings.js`
- **Views**: `session/`, `match/`, `ranking/`
- **Components**: `components/match/`

모든 파일은 stub으로 구현되어 있으며, Phase 2에서 실제 기능을 추가하면 됩니다.
