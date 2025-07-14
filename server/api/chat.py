# server/api/chat.py (수정 후)

from fastapi import APIRouter, Request
from pydantic import BaseModel
from server.agents.state import AgentState
from typing import List

router = APIRouter()

class ChatRequest(BaseModel):
    """채팅 요청을 위한 Pydantic 모델입니다."""
    query: str
    history: List[str] = []

@router.post("/chat")
async def chat_endpoint(request_data: ChatRequest, request: Request):
    """
    채팅 요청을 받아 LangGraph 워크플로우를 실행하고 결과를 반환하는 API 엔드포인트.
    """
    # --- 개선: 매번 그래프를 컴파일하는 대신, 시작 시 생성된 앱을 사용 ---
    app = request.app.state.langgraph_app
    # --- 개선 끝 ---

    # 입력 데이터 준비
    inputs = AgentState(query=request_data.query, history=request_data.history, response="", documents=[])

    # 워크플로우 실행
    final_state = app.invoke(inputs)

    return {"response": final_state.get("response", "오류가 발생했습니다. 응답을 생성하지 못했습니다.")}