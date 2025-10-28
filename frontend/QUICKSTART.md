# 빠른 시작 가이드

## 5분 안에 실행하기

### 1단계: 의존성 설치 (최초 1회)

```bash
cd /Users/moonsuk/ssos/frontend
npm install
```

**예상 시간**: 2-3분

### 2단계: 백엔드 서버 확인

다른 터미널에서 백엔드가 실행 중인지 확인:

```bash
curl http://localhost:8000/docs
```

백엔드가 실행 중이 아니면:

```bash
cd /Users/moonsuk/ssos/backend
uvicorn app.main:app --reload
```

### 3단계: 프론트엔드 실행

```bash
npm run dev
```

**서버 주소**: http://localhost:3000

### 4단계: 브라우저에서 접속

1. Chrome/Firefox/Safari 에서 http://localhost:3000 접속
2. 회원가입 페이지에서 첫 계정 생성
3. 로그인

## 테스트 계정 (백엔드에 미리 생성된 경우)

```
사용자명: admin
비밀번호: admin123
```

## 첫 동호회 만들기

1. 로그인 후 상단바에서 "동호회 관리" 클릭 (관리자만)
2. 왼쪽 폼에서 동호회 정보 입력:
   - 동호회명: "서울 테니스 클럽"
   - 설명: "매주 토요일 모임"
   - 위치: "서울 강남구 테니스장"
3. "생성" 버튼 클릭
4. 상단바에서 생성된 동호회 선택

## 첫 회원 추가하기

1. 사이드 메뉴에서 "회원 관리" 클릭 (관리자만)
2. 왼쪽 폼에서 회원 정보 입력:
   - 사용자 ID: 1 (회원가입한 사용자의 ID)
   - 성별: 선택
   - 선호 타입: 선택
3. "추가" 버튼 클릭
4. 오른쪽에 추가된 회원 확인

## 주요 기능 살펴보기

### 동호회
- **목록**: 사이드 메뉴 > "동호회 목록"
- **상세**: 동호회 카드 클릭
- **관리**: 사이드 메뉴 > "동호회 관리" (관리자)

### 회원
- **목록**: 사이드 메뉴 > "회원 목록"
- **검색**: 상단 검색창에 이름 입력
- **필터**: 성별, 선호 타입 드롭다운
- **관리**: 사이드 메뉴 > "회원 관리" (관리자)

### 내 정보
- 우측 상단 프로필 아이콘 클릭
- 로그아웃: 메뉴에서 "로그아웃"

## 문제 해결

### 포트 충돌

```bash
# vite.config.js에서 포트 변경
server: {
  port: 3001,
}
```

### CORS 에러

백엔드 FastAPI에서 CORS 설정 확인:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 로그인 안됨

1. 백엔드 서버 실행 확인
2. 브라우저 콘솔에서 네트워크 에러 확인
3. 사용자명/비밀번호 확인

### 동호회 선택 안됨

1. F5로 페이지 새로고침
2. 로그아웃 후 다시 로그인
3. 브라우저 캐시 삭제

## 개발 팁

### Hot Reload
- 파일 수정 시 자동으로 브라우저 새로고침
- 저장만 하면 즉시 반영

### Vue Devtools
- Chrome 확장 프로그램 설치 권장
- Pinia 스토어 상태 실시간 확인

### API 테스트
- 백엔드 API 문서: http://localhost:8000/docs
- Swagger UI에서 직접 API 테스트 가능

## 다음 단계

Phase 1 완료 ✅

**Phase 2에서 추가될 기능**:
- 세션 생성 및 관리
- 자동 매칭 시스템
- 경기 결과 입력
- 랭킹 시스템

## 도움말

- [README.md](./README.md) - 프로젝트 소개
- [INSTALL.md](./INSTALL.md) - 상세 설치 가이드
- [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) - 구조 설명
- [SUMMARY.md](./SUMMARY.md) - Phase 1 요약

## 지원

문제가 발생하면 프로젝트 저장소의 이슈를 등록해주세요.

---

**Happy Coding! 🎾**
