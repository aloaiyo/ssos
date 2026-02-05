"""
FastAPI 애플리케이션 엔트리포인트
"""
import logging

# 로깅 설정 - app 모듈의 로거를 INFO 레벨로 설정
logging.basicConfig(level=logging.INFO)
logging.getLogger("app").setLevel(logging.INFO)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from app.config import settings, TORTOISE_ORM
from app.api import auth, clubs, members, events, sessions, matches, rankings, users, announcements, fees, guests, seasons, ocr

# FastAPI 앱 생성
app = FastAPI(
    title=settings.APP_NAME,
    description="테니스 동호회 관리 시스템 API",
    version="1.0.0",
    debug=settings.DEBUG
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth.router, prefix="/api")
app.include_router(clubs.router, prefix="/api")
app.include_router(members.router, prefix="/api")
app.include_router(events.router, prefix="/api")
app.include_router(sessions.router, prefix="/api")
app.include_router(matches.router, prefix="/api")
app.include_router(rankings.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(announcements.router, prefix="/api")
app.include_router(fees.router, prefix="/api")
app.include_router(guests.router, prefix="/api")
app.include_router(seasons.router, prefix="/api")
app.include_router(ocr.router, prefix="/api")

# Tortoise ORM 등록
register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=False,  # aerich 마이그레이션 사용
    add_exception_handlers=True,
)


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "테니스 동호회 관리 시스템 API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
