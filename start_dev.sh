#!/bin/bash

# 색상 정의
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎾 테니스 동호회 관리 시스템 개발 서버 시작...${NC}"

# 백엔드 시작
echo -e "${GREEN}🚀 백엔드 서버 시작 중...${NC}"
cd backend
# 백그라운드에서 실행하고 PID 저장
poetry run uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# 프론트엔드 시작
echo -e "${GREEN}🚀 프론트엔드 서버 시작 중...${NC}"
cd frontend
# 백그라운드에서 실행하고 PID 저장
npm run dev &
FRONTEND_PID=$!
cd ..

echo -e "${BLUE}✅ 서버가 실행되었습니다!${NC}"
echo -e "   - Backend: http://localhost:8000"
echo -e "   - Frontend: http://localhost:3000"
echo -e "${BLUE}종료하려면 Ctrl+C를 누르세요.${NC}"

# 종료 시그널 처리
trap "kill $BACKEND_PID $FRONTEND_PID; exit" SIGINT SIGTERM

# 프로세스 대기
wait
