# 빠른 시작 가이드

## 필수 요구사항

- Python 3.11 이상
- PostgreSQL 13 이상
- Poetry

## 설치 단계

### 1. Poetry 설치 (필요한 경우)

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 2. 프로젝트 디렉토리로 이동

```bash
cd /Users/moonsuk/ssos/backend
```

### 3. 가상환경 생성 및 의존성 설치

```bash
poetry install
```

### 4. PostgreSQL 데이터베이스 생성

```bash
# PostgreSQL에 접속
psql -U postgres

# 데이터베이스 생성
CREATE DATABASE tennis_club;

# 종료
\q
```

또는 명령줄에서:

```bash
createdb -U postgres tennis_club
```

### 5. 환경 변수 설정

`.env` 파일이 이미 생성되어 있습니다. 필요에 따라 수정하세요:

```bash
vi .env
```

**중요**: 프로덕션 환경에서는 반드시 `SECRET_KEY`를 변경하세요!

### 6. 데이터베이스 마이그레이션 초기화

```bash
# Aerich 초기화
poetry run aerich init -t app.config.TORTOISE_ORM

# 초기 마이그레이션 생성
poetry run aerich init-db
```

### 7. 서버 실행

```bash
# 개발 서버 실행 (자동 재시작)
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

또는:

```bash
poetry run python -m app.main
```

### 8. API 문서 확인

브라우저에서 다음 URL을 열어 API 문서를 확인하세요:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 테스트 데이터 생성

### 1. 사용자 등록

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "password123",
    "name": "관리자"
  }'
```

### 2. 로그인

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=password123"
```

응답에서 `access_token`을 복사하세요.

### 3. 동호회 생성

```bash
curl -X POST "http://localhost:8000/api/clubs" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "name": "서울 테니스 동호회",
    "description": "주말마다 모이는 즐거운 테니스 동호회입니다"
  }'
```

## 문제 해결

### PostgreSQL 연결 오류

```
tortoise.exceptions.DBConnectionError
```

**해결방법**:
1. PostgreSQL이 실행 중인지 확인: `pg_isready`
2. `.env` 파일의 `DATABASE_URL` 확인
3. 데이터베이스가 존재하는지 확인: `psql -U postgres -l`

### 포트 충돌

```
Address already in use
```

**해결방법**:
1. 다른 포트 사용: `--port 8001`
2. 또는 실행 중인 프로세스 종료: `lsof -ti:8000 | xargs kill`

### 마이그레이션 오류

```
aerich.exceptions.AerichException
```

**해결방법**:
1. `migrations` 폴더 삭제
2. 마이그레이션 재초기화:
   ```bash
   rm -rf migrations
   poetry run aerich init -t app.config.TORTOISE_ORM
   poetry run aerich init-db
   ```

## 개발 팁

### 1. 자동 재시작 활성화

```bash
poetry run uvicorn app.main:app --reload
```

### 2. 로그 레벨 설정

```bash
poetry run uvicorn app.main:app --log-level debug
```

### 3. 특정 호스트/포트 지정

```bash
poetry run uvicorn app.main:app --host 127.0.0.1 --port 8080
```

### 4. 데이터베이스 스키마 확인

```bash
psql -U postgres -d tennis_club -c "\dt"
```

### 5. 마이그레이션 히스토리

```bash
poetry run aerich history
```

## 다음 단계

1. ✅ 백엔드 서버 실행
2. 🔄 프론트엔드 개발 시작
3. 🔄 API 통합 테스트
4. 🔄 매칭 알고리즘 개선
5. 🔄 프로덕션 배포 준비

## 추가 리소스

- FastAPI 문서: https://fastapi.tiangolo.com/
- Tortoise-ORM 문서: https://tortoise.github.io/
- Aerich 문서: https://github.com/tortoise/aerich
- PostgreSQL 문서: https://www.postgresql.org/docs/
