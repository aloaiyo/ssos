# 테니스 동호회 관리 시스템 - 프론트엔드

Vue 3 + Vuetify 3 기반 테니스 동호회 관리 시스템 프론트엔드

## 기술 스택

- Vue 3 (Composition API)
- Vuetify 3 (Material Design)
- Pinia (상태 관리)
- Vue Router (라우팅)
- Axios (HTTP 클라이언트)
- Day.js (날짜 처리)
- Vite (빌드 도구)

## 설치 및 실행

```bash
# 의존성 설치
npm install

# 개발 서버 실행 (http://localhost:3000)
npm run dev

# 프로덕션 빌드
npm run build

# 프로덕션 프리뷰
npm run preview
```

## 프로젝트 구조

```
src/
├── main.js              # 앱 엔트리포인트
├── App.vue              # 루트 컴포넌트
├── router/              # 라우팅
├── stores/              # Pinia 스토어
├── api/                 # API 클라이언트
├── components/          # 공통 컴포넌트
├── views/               # 페이지 컴포넌트
├── plugins/             # Vue 플러그인
├── styles/              # 스타일
└── utils/               # 유틸리티
```

## 환경 변수

`.env` 파일에서 설정:

```
VITE_API_BASE_URL=http://localhost:8000
```

## Phase 1 구현 완료

- ✅ 프로젝트 초기화
- ✅ Vuetify 3 설정
- ✅ 라우터 및 스토어 구조
- ✅ 로그인/회원가입
- ✅ 동호회 관리
- ✅ 회원 관리
- ✅ 기본 레이아웃

## Phase 2 예정

- 세션 관리
- 매칭 시스템
- 결과 입력
- 랭킹 표시
