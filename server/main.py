from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.api import chat
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

app = FastAPI(
    title="AI Assistant Server",
    description="Groq과 HuggingFace를 사용하는 AI 비서 백엔드 API",
    version="1.0.0",
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 프로덕션 환경에서는 특정 도메인만 허용하세요.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 포함
app.include_router(chat.router, prefix="/api")

@app.get("/")
def read_root():
    """서버 루트 경로에 대한 기본 응답을 반환합니다."""
    return {"message": "AI Assistant 서버가 실행 중입니다."}
