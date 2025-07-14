from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from server.core.config import settings
from langchain_groq import ChatGroq

# 공통 LLM 초기화 (Groq으로 변경)
llm = ChatGroq(
    groq_api_key=settings.GROQ_API_KEY,
    model_name=settings.GROQ_MODEL_NAME,
    temperature=0,
    streaming=True,
)

# RAG 체인
RAG_PROMPT = """
당신은 사용자의 질문에 대해 주어진 문서를 기반으로 답변하는 AI 어시스턴트입니다.
문서 내용을 충실하게 사용하여, 마치 해당 내용을 원래 알고 있었던 것처럼 자연스럽게 설명해주세요.
문서에 없는 내용은 답변에 포함시키지 마세요.

[문서]
{context}

[질문]
{question}
"""
rag_prompt_template = ChatPromptTemplate.from_template(RAG_PROMPT)
rag_chain = rag_prompt_template | llm | StrOutputParser()

# 일반 대화 체인
GENERAL_PROMPT = """
당신은 사용자와 자유롭게 대화하는 친절한 AI 어시스턴트입니다.
사용자의 질문에 대해 간결하고 명확하게 답변해주세요.

[대화 기록]
{history}

[사용자 질문]
{question}
"""
general_prompt_template = ChatPromptTemplate.from_template(GENERAL_PROMPT)
general_chain = general_prompt_template | llm | StrOutputParser()
