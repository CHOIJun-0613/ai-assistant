#### **`server/main.py`**

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.api import chat
import os
from dotenv import load_dotenv
import uvicorn
from langgraph.graph import StateGraph, END
from server.agents.state import AgentState
from server.agents.master_agent import route_request

# .env 파일에서 환경 변수 로드
load_dotenv()

# --- 개선: 애플리케이션 생명주기 동안 사용할 앱 인스턴스 ---
app = FastAPI(
    title="AI Assistant Server",
    description="Groq과 HuggingFace를 사용하는 AI 비서 백엔드 API",
    version="1.0.0",
)

# --- 개선: LangGraph 앱을 시작 시 한 번만 컴파일 ---
workflow = StateGraph(AgentState)
workflow.add_node("router", route_request)
workflow.set_entry_point("router")
workflow.add_edge("router", END)
langgraph_app = workflow.compile()

# FastAPI의 state에 langgraph_app 저장
app.state.langgraph_app = langgraph_app
# --- 개선 끝 ---

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

# --- 개선: 표준적인 uvicorn 실행 방식 추가 ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
# --- 개선 끝 ---