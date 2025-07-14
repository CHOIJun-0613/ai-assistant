from fastapi import APIRouter
from pydantic import BaseModel
from langgraph.graph import StateGraph, END
from server.agents.state import AgentState
from server.agents.master_agent import route_request
from typing import List

router = APIRouter()

class ChatRequest(BaseModel):
    """채팅 요청을 위한 Pydantic 모델입니다."""
    query: str
    history: List[str] = []

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    채팅 요청을 받아 LangGraph 워크플로우를 실행하고 결과를 반환하는 API 엔드포인트.
    """
    # LangGraph 워크플로우 정의
    workflow = StateGraph(AgentState)
    
    # 노드 정의
    workflow.add_node("router", route_request)
    
    # 그래프 빌드
    workflow.set_entry_point("router")
    workflow.add_edge("router", END)
    
    # 그래프 컴파일
    app = workflow.compile()
    
    # 입력 데이터 준비
    inputs = AgentState(query=request.query, history=request.history, response="", documents=[])
    
    # 워크플로우 실행
    final_state = app.invoke(inputs)
    
    return {"response": final_state["response"]}
