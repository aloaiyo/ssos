# 🎾 테니스 동호회 관리 시스템

테니스 동호회를 위한 종합 관리 웹 서비스입니다. 회원 관리, 일정 관리, 자동 게임 매칭, 결과 기록, 랭킹 시스템을 제공합니다.

## 📋 목차

- [주요 기능](#주요-기능)
- [기술 스택](#기술-스택)
- [프로젝트 구조](#프로젝트-구조)
- [시작하기](#시작하기)
- [개발 가이드](#개발-가이드)
- [배포](#배포)
- [라이선스](#라이선스)

## 🎯 주요 기능

### 회원 관리
- ✅ 동호회 생성 및 관리 (슈퍼 관리자)
- ✅ 회원 등록 및 프로필 관리
- ✅ 역할 기반 권한 관리 (관리자/일반 회원)
- ✅ 여러 동호회 가입 지원

### 일정 관리
- 📅 정기/비정기 모임 생성
- ⏰ 세션별 시간 설정 (시작/종료 시간)
- 🏟️ 코트 수 설정
- 👥 참가자 관리

### 자동 매칭 시스템 ⚡ 핵심
- 🤖 자동 게임 매칭 생성
- ⚖️ 공평한 경기 수 배분
- 🎾 복식/혼합복식/단식 지원
- ✏️ 수동 매칭 수정 가능
- 📊 공평성 지표 제공

### 결과 및 랭킹
- 📝 경기 결과 입력 (세트 스코어)
- 🏆 실시간 랭킹 업데이트
- 📈 개인 통계 (승률, 전적)
- 🎖️ 승점제 랭킹 (승3점/무1점/패0점)

### 추가 기능 (예정)
- 🤝 동호회 간 교류전
- 📱 모바일 앱
- 📧 알림 시스템
- 📊 고급 통계 대시보드

## 🛠 기술 스택

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: Tortoise-ORM
- **Database**: PostgreSQL
- **Migration**: Aerich
- **Authentication**: JWT (python-jose)
- **Security**: Passlib (bcrypt)
- **Package Manager**: Poetry

### Frontend
- **Framework**: Vue 3 (Composition API)
- **UI Library**: Vuetify 3
- **State Management**: Pinia
- **Routing**: Vue Router
- **HTTP Client**: Axios
- **Date Library**: Day.js
- **Build Tool**: Vite

### Infrastructure
- **Frontend Hosting**: AWS S3 + CloudFront
- **Backend**: AWS EC2 (Docker)
- **Database**: AWS RDS (PostgreSQL)
- **CI/CD**: GitHub Actions (예정)

## 📁 프로젝트 구조

```
ssos/
├── backend/              # FastAPI 백엔드
│   ├── app/
│   │   ├── models/      # Tortoise-ORM 모델
│   │   ├── schemas/     # Pydantic 스키마
│   │   ├── api/         # API 엔드포인트
│   │   ├── services/    # 비즈니스 로직
│   │   └── core/        # 인증, 보안
│   ├── migrations/      # Aerich 마이그레이션
│   ├── pyproject.toml
│   └── README.md
│
├── frontend/            # Vue 3 프론트엔드
│   ├── src/
│   │   ├── views/       # 페이지 컴포넌트
│   │   ├── components/  # 재사용 컴포넌트
│   │   ├── stores/      # Pinia 스토어
│   │   ├── api/         # API 클라이언트
│   │   └── router/      # Vue Router
│   ├── package.json
│   └── README.md
│
└── README.md            # 이 파일
```

## 🚀 시작하기

### 사전 요구사항

- Python 3.11 이상
- Node.js 18 이상
- PostgreSQL 13 이상
- Poetry (Python 패키지 관리)
- npm 또는 yarn

### 1. 저장소 클론

```bash
git clone <repository-url>
cd ssos
```

### 2. 백엔드 설정

```bash
# backend 디렉토리로 이동
cd backend

# Poetry로 의존성 설치
poetry install

# 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 데이터베이스 정보 입력

# PostgreSQL 데이터베이스 생성
createdb tennis_club

# 마이그레이션 초기화
poetry run aerich init -t app.config.TORTOISE_ORM
poetry run aerich init-db

# 개발 서버 실행
poetry run uvicorn app.main:app --reload
```

백엔드 서버: http://localhost:8000
API 문서: http://localhost:8000/docs

### 3. 프론트엔드 설정

```bash
# frontend 디렉토리로 이동 (새 터미널)
cd frontend

# 의존성 설치
npm install

# 환경 변수 설정 (.env 파일이 이미 생성되어 있음)
# 필요시 백엔드 URL 수정

# 개발 서버 실행
npm run dev
```

프론트엔드 서버: http://localhost:3000

### 4. 초기 데이터 설정

1. 백엔드 서버에서 슈퍼 관리자 계정 생성
2. 프론트엔드에서 로그인
3. 동호회 생성
4. 회원 등록

## 💻 개발 가이드

### Backend 개발

```bash
cd backend

# 새 마이그레이션 생성
poetry run aerich migrate --name "description"

# 마이그레이션 적용
poetry run aerich upgrade

# 테스트 실행 (예정)
poetry run pytest

# 코드 포맷팅
poetry run black .
poetry run isort .
```

**주요 파일**:
- `app/models/`: 데이터베이스 모델 정의
- `app/api/`: API 엔드포인트 구현
- `app/services/`: 비즈니스 로직 (매칭 알고리즘 등)
- `app/schemas/`: API 요청/응답 스키마

### Frontend 개발

```bash
cd frontend

# 개발 서버 (핫 리로드)
npm run dev

# 프로덕션 빌드
npm run build

# 빌드 미리보기
npm run preview

# 코드 린트
npm run lint
```

**주요 디렉토리**:
- `src/views/`: 페이지 컴포넌트
- `src/components/`: 재사용 컴포넌트
- `src/stores/`: 상태 관리 (Pinia)
- `src/api/`: 백엔드 API 클라이언트

### 코딩 규칙

**Backend**:
- Python 3.11+ 타입 힌트 필수
- Pydantic V2 스키마 사용
- 모든 주요 코드에 한글 주석
- API는 RESTful 원칙 준수

**Frontend**:
- Vue 3 Composition API (`<script setup>`)
- Vuetify 3 컴포넌트 우선 사용
- 반응형 디자인 필수 (모바일 퍼스트)
- 모든 텍스트 한글로 표시

## 🎨 디자인 시스템

### 컬러 팔레트
```javascript
{
  primary: '#1976D2',    // 블루 - 주요 액션
  secondary: '#424242',  // 다크 그레이 - 보조 요소
  accent: '#FF9800',     // 오렌지 - 강조
  success: '#4CAF50',    // 그린 - 성공, 승리
  warning: '#FFC107',    // 옐로우 - 주의
  error: '#F44336',      // 레드 - 에러, 패배
}
```

### 타이포그래피
- 폰트: Noto Sans KR
- 제목: 24px, bold
- 본문: 16px, regular
- 캡션: 14px, light

## 📦 배포

### Backend (AWS EC2)

```bash
# Docker 이미지 빌드
docker build -t tennis-club-backend .

# EC2에서 실행
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  tennis-club-backend
```

### Frontend (AWS S3 + CloudFront)

```bash
# 프로덕션 빌드
npm run build

# S3에 업로드
aws s3 sync dist/ s3://your-bucket-name/

# CloudFront 캐시 무효화
aws cloudfront create-invalidation \
  --distribution-id YOUR_DIST_ID \
  --paths "/*"
```

## 🔐 보안

- JWT 토큰 기반 인증
- bcrypt 비밀번호 해싱
- CORS 설정으로 출처 제한
- SQL 인젝션 방지 (ORM 사용)
- XSS 방지 (Vue의 자동 이스케이핑)

## 🧪 테스트 (예정)

### Backend
```bash
poetry run pytest
poetry run pytest --cov=app
```

### Frontend
```bash
npm run test
npm run test:coverage
```

## 📝 API 문서

백엔드 서버 실행 후:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

주요 엔드포인트:
- `POST /api/auth/login` - 로그인
- `GET /api/clubs` - 동호회 목록
- `POST /api/clubs/{club_id}/members` - 회원 추가
- `POST /api/sessions/{session_id}/matches/generate` - 자동 매칭 생성
- `GET /api/rankings` - 랭킹 조회

## 🗺️ 로드맵

### Phase 1 (완료) ✅
- [x] 기본 인프라 구축
- [x] 인증 시스템
- [x] 동호회 관리
- [x] 회원 관리
- [x] 기본 UI 레이아웃

### Phase 2 (진행 중) 🚧
- [ ] 세션 생성 및 관리
- [ ] 자동 매칭 시스템
- [ ] 결과 입력
- [ ] 랭킹 시스템

### Phase 3 (예정) 📋
- [ ] 매칭 알고리즘 최적화
- [ ] 드래그 앤 드롭 매칭 수정
- [ ] 고급 통계 대시보드
- [ ] 교류전 기능

### Phase 4 (예정) 🔮
- [ ] 모바일 앱 (React Native)
- [ ] 푸시 알림
- [ ] 실시간 업데이트 (WebSocket)
- [ ] 사진 업로드

## 🤝 기여

기여를 환영합니다! 다음 절차를 따라주세요:

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다.

## 👥 팀

- **Backend**: backend-architect 페르소나
- **Frontend**: frontend-architect 페르소나
- **Product Owner**: moonsuk

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해주세요.

---

**Built with ❤️ for Tennis Community**

🎾 **Last Updated**: 2025-10-28
📍 **Version**: 0.1.0 (Phase 1)
🚀 **Status**: Active Development
