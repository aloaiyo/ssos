# 🚀 빠른 시작 가이드

테니스 동호회 관리 시스템을 5분 안에 실행해보세요!

## 📋 준비물 체크리스트

- [ ] Python 3.11 이상
- [ ] Node.js 18 이상
- [ ] PostgreSQL 13 이상 (실행 중)
- [ ] Poetry (`pip install poetry`)
- [ ] 약 15분의 시간

## ⚡ 빠른 실행 (3단계)

### 1단계: 데이터베이스 준비

```bash
# PostgreSQL 데이터베이스 생성
createdb tennis_club

# 또는 psql로 생성
psql -U postgres
CREATE DATABASE tennis_club;
\q
```

### 2단계: 백엔드 실행

```bash
cd backend

# 의존성 설치 (최초 1회)
poetry install

# 환경 변수 설정
cat > .env << EOF
DATABASE_URL=postgres://postgres:password@localhost:5432/tennis_club
SECRET_KEY=your-secret-key-here-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF

# 마이그레이션
poetry run aerich init -t app.config.TORTOISE_ORM
poetry run aerich init-db

# 서버 실행
poetry run uvicorn app.main:app --reload
```

✅ 백엔드 실행 완료! http://localhost:8000/docs

### 3단계: 프론트엔드 실행

**새 터미널**을 열고:

```bash
cd frontend

# 의존성 설치 (최초 1회)
npm install

# 개발 서버 실행
npm run dev
```

✅ 프론트엔드 실행 완료! http://localhost:3000

## 🎯 첫 사용

### 1. 회원가입 및 로그인

1. 브라우저에서 http://localhost:3000 접속
2. "회원가입" 클릭
3. 정보 입력 후 가입
4. 로그인

### 2. 동호회 생성 (슈퍼 관리자)

```bash
# 백엔드 터미널에서 슈퍼 관리자 계정 생성
poetry run python -c "
from app.models.user import User
from app.core.security import get_password_hash
import asyncio

async def create_admin():
    await Tortoise.init(
        db_url='postgres://postgres:password@localhost:5432/tennis_club',
        modules={'models': ['app.models']}
    )
    user = await User.create(
        email='admin@tennis.com',
        password_hash=get_password_hash('admin123'),
        name='관리자',
        is_super_admin=True
    )
    print(f'슈퍼 관리자 생성: {user.email}')
    await Tortoise.close_connections()

asyncio.run(create_admin())
"
```

**또는** 직접 회원가입 후 데이터베이스에서 `is_super_admin` 플래그 활성화:

```sql
UPDATE users SET is_super_admin = true WHERE email = 'your@email.com';
```

### 3. 동호회 생성

1. 슈퍼 관리자로 로그인
2. "동호회 관리" 메뉴
3. "새 동호회" 버튼 클릭
4. 동호회 정보 입력

### 4. 회원 추가

1. 동호회 선택
2. "회원 관리" 메뉴
3. "새 회원" 버튼
4. 회원 정보 입력 (이름, 성별, 선호 타입)

## 🔧 문제 해결

### 백엔드가 실행되지 않아요

**문제**: `ModuleNotFoundError`
```bash
# 해결: Poetry 환경 재설치
cd backend
poetry install --no-root
```

**문제**: 데이터베이스 연결 오류
```bash
# 해결: PostgreSQL 실행 확인
pg_isready

# PostgreSQL 실행
# macOS
brew services start postgresql

# Ubuntu
sudo service postgresql start
```

**문제**: 마이그레이션 오류
```bash
# 해결: 마이그레이션 초기화
rm -rf migrations/
poetry run aerich init -t app.config.TORTOISE_ORM
poetry run aerich init-db
```

### 프론트엔드가 실행되지 않아요

**문제**: `npm install` 오류
```bash
# 해결: 캐시 삭제 후 재설치
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**문제**: 백엔드 API 연결 안됨
```bash
# .env 파일 확인
cat .env

# VITE_API_BASE_URL이 http://localhost:8000 인지 확인
```

**문제**: Vuetify 컴포넌트 표시 안됨
```bash
# 해결: 브라우저 캐시 삭제 (Ctrl+Shift+R)
# 또는 시크릿 모드로 접속
```

### 포트가 이미 사용 중이에요

**백엔드** (8000 포트):
```bash
# 포트 사용 프로세스 확인
lsof -i :8000

# 프로세스 종료
kill -9 <PID>

# 또는 다른 포트 사용
poetry run uvicorn app.main:app --port 8001 --reload
```

**프론트엔드** (3000 포트):
```bash
# vite.config.js 수정
export default defineConfig({
  server: {
    port: 3001  // 다른 포트로 변경
  }
})
```

## 📊 동작 확인

### 백엔드 체크

```bash
# API 서버 헬스 체크
curl http://localhost:8000/

# API 문서 확인
open http://localhost:8000/docs
```

### 프론트엔드 체크

```bash
# 개발 서버 확인
curl http://localhost:3000

# 브라우저 콘솔에서 API 연결 확인
# F12 → Console → 에러 메시지 확인
```

## 🎓 다음 단계

축하합니다! 시스템이 실행되었습니다. 이제 다음을 진행하세요:

1. ✅ **회원 추가**: 10-20명의 테스트 회원 생성
2. ✅ **일정 생성**: 첫 번째 모임 일정 만들기
3. 🚧 **세션 생성**: Phase 2 개발 필요
4. 🚧 **매칭 생성**: Phase 2 개발 필요

## 📚 추가 자료

- [전체 README](./README.md) - 프로젝트 전체 개요
- [백엔드 문서](./backend/README.md) - API 상세 문서
- [프론트엔드 문서](./frontend/README.md) - UI 컴포넌트 가이드
- [프로젝트 구조](./backend/PROJECT_STRUCTURE.md) - 코드 구조 설명

## 💬 도움이 필요하신가요?

- 🐛 버그 발견: GitHub Issues에 등록
- 💡 기능 제안: GitHub Discussions에 게시
- 📧 직접 문의: 프로젝트 관리자에게 연락

---

**즐거운 테니스 되세요!** 🎾
