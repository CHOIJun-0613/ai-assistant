# 🚀 AI Assistant Project (Groq & RAG & Google Tools)

핵심 AI 모델을 Groq의 초고속 언어 모델(LPU)과 HuggingFace의 오픈소스 임베딩 모델로 전환하여 구현한 AI 업무 자동화 비서 애플리케이션입니다.

Llama 3와 같은 고성능 오픈소스 LLM을 Groq API를 통해 사용하여, 비용 효율적이고 빠른 응답 속도를 경험할 수 있습니다. 
또한, 한국어 환경에 특화된 오픈소스 임베딩 모델을 활용하여 RAG(검색 증강 생성) 성능을 최적화하고, 
Google Workspace(Gmail, Calendar) 도구를 연동하여 실제 업무 생산성을 극대화합니다.

## 🌟 주요 특징

- **🚀 초고속 LLM 추론**: Groq 클라우드의 LPU(Language Processing Unit)를 활용하여 실시간에 가까운 응답 속도를 제공합니다.
- **🔄 유연한 모델 선택**: `llama3-8b-8192`, `mixtral-8x7b-32768` 등 Groq이 제공하는 다양한 최신 오픈소스 LLM을 손쉽게 변경하여 사용할 수 있습니다.
- **🇰🇷 한국어 특화 RAG**: `jhgan/ko-sbert-nli`와 같은 HuggingFace의 고성능 한국어 임베딩 모델을 사용하여 로컬 문서 검색 및 요약의 정확도를 높였습니다.
- **🛠️ Google 도구 연동**: Gmail, Google Calendar 등 Google Workspace 도구를 활용하는 에이전트 기능을 통해 이메일 검색, 일정 조회 등 실제 업무를 처리할 수 있습니다.
- **🧩 확장 가능한 아키텍처**: LangChain과 LangGraph를 기반으로 설계되어, 새로운 도구나 전문가 에이전트를 손쉽게 추가할 수 있는 유연한 구조를 가집니다.

## ⚙️ 시스템 아키텍처

이 시스템은 사용자의 요청을 받아 의도를 파악하고, 가장 적절한 도구를 동적으로 선택하여 작업을 수행하는 에이전트 기반으로 설계되었습니다.

1.  **User Interface (Streamlit)**: 사용자는 웹 기반 인터페이스를 통해 AI 비서에게 작업을 요청합니다.
2.  **Backend (FastAPI)**: API 서버는 사용자 요청을 받아 LangGraph로 구성된 에이전트 워크플로우를 실행합니다.
3.  **Agent Executor (LangGraph)**: 사용자의 요청을 분석하여 '마스터 에이전트'가 적절한 '전문가 에이전트'나 도구를 동적으로 선택하고 실행합니다.
4.  **Language Model (Groq)**: `ChatGroq`을 통해 Llama 3와 같은 언어 모델을 호출하여 사용자의 의도를 파악하고, 최종 응답을 생성합니다.
5.  **Tools**:
    -   **RAG Retriever**: 로컬 `documents` 폴더의 텍스트 파일을 FAISS 벡터 저장소에 인덱싱하고, HuggingFace 임베딩을 사용하여 관련 문서를 검색합니다.
    -   **Google Tools**: OAuth2 인증을 통해 사용자의 Gmail, Google Calendar 데이터를 안전하게 조회하고 관련 작업을 수행합니다.
6.  **Vector Store (FAISS)**: HuggingFace 임베딩으로 변환된 문서 벡터를 저장하고 빠른 검색을 지원합니다.

## 🚀 시작하기

### 1. 사전 준비

-   Python 3.8 이상
-   Google Cloud Platform 프로젝트 및 OAuth 클라이언트 ID. (`credentials.json` 파일)
-   Groq API 키

### 2. 설치

```bash
# 1. 프로젝트 클론
git clone [https://github.com/choijun-0613/ai-assistant.git](https://github.com/choijun-0613/ai-assistant.git)
cd ai-assistant

# 2. 필요한 라이브러리 설치
pip install -r requirements.txt

# 3. 환경 변수 설정
# .env 파일을 생성하고 아래 내용을 채워넣으세요.
# (보안을 위해 .gitignore에 등록되어 있습니다)
cp .env.example .env


# 'documents' 폴더의 텍스트 파일을 기반으로 FAISS 벡터 저장소를 생성합니다.(처음 1회만 생성)
python -m server.rag.ingest

# FastAPI 백엔드 서버를 실행합니다.
uvicorn server.main:app --reload

# Streamlit 프론트엔드 클라이언트를 실행합니다.
streamlit run app/app.py