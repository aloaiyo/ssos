# 설치 및 실행 가이드

## 사전 요구사항

- Node.js 18.x 이상
- npm 9.x 이상

## 설치 방법

### 1. 의존성 설치

```bash
cd frontend
npm install
```

### 2. 환경 변수 설정

`.env` 파일이 이미 생성되어 있습니다:

```
VITE_API_BASE_URL=http://localhost:8000
```

백엔드 API 주소가 다르면 수정하세요.

### 3. 개발 서버 실행

```bash
npm run dev
```

브라우저에서 http://localhost:3000 으로 접속합니다.

### 4. 프로덕션 빌드

```bash
npm run build
```

빌드 결과물은 `dist/` 디렉토리에 생성됩니다.

### 5. 프로덕션 프리뷰

```bash
npm run preview
```

## 초기 계정 생성

1. 회원가입 페이지에서 첫 계정을 생성합니다.
2. 백엔드에서 해당 계정에 admin 또는 super_admin 권한을 부여합니다.
3. 로그인 후 동호회를 생성하고 회원을 추가합니다.

## 문제 해결

### CORS 에러가 발생하는 경우

백엔드 FastAPI 서버에서 CORS 설정을 확인하세요:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 포트가 이미 사용 중인 경우

`vite.config.js`에서 포트를 변경하세요:

```javascript
export default defineConfig({
  server: {
    port: 3001, // 원하는 포트로 변경
  },
})
```

### 의존성 설치 오류

캐시를 삭제하고 다시 설치합니다:

```bash
rm -rf node_modules package-lock.json
npm install
```

## 개발 팁

### 핫 리로드

개발 서버는 자동으로 핫 리로드를 지원합니다. 파일을 수정하면 즉시 브라우저에 반영됩니다.

### Vue Devtools

Chrome 확장 프로그램 "Vue.js devtools"를 설치하면 디버깅이 편리합니다.

### API 테스트

백엔드 API 문서는 http://localhost:8000/docs 에서 확인할 수 있습니다.

## Phase 1 완료 기능

✅ 프로젝트 초기화 (Vite + Vue 3)
✅ Vuetify 3 설정
✅ 라우터 및 스토어 구조
✅ 로그인/회원가입 화면
✅ 동호회 목록/생성/수정/삭제
✅ 회원 목록/추가/수정/삭제
✅ 기본 레이아웃 (AppBar, NavigationDrawer, Footer)

## Phase 2 예정 기능

- 세션 생성 및 관리
- 자동 매칭 시스템
- 경기 결과 입력
- 랭킹 시스템
