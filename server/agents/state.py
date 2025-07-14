from typing import List, TypedDict

class AgentState(TypedDict):
    """
    에이전트의 상태를 정의하는 TypedDict.
    - query: 사용자의 원본 질문
    - response: 최종 생성된 응답
    - history: 대화 기록
    - documents: RAG를 통해 검색된 문서
    """
    query: str
    response: str
    history: List[str]
    documents: List[str]
