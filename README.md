# AI Assistant Project (with Groq & HuggingFace)

이 프로젝트는 `ai-assist-google` 프로젝트의 구조를 기반으로, 핵심 AI 모델을 Groq의 초고속 언어 모델(LPU 기반)과 HuggingFace의 오픈소스 임베딩 모델로 전환한 AI 업무 자동화 비서 애플리케이션입니다.

기존 Google Gemini 모델 대신 Llama 3와 같은 고성능 오픈소스 LLM을 Groq API를 통해 사용함으로써, 비용 효율적이고 빠른 응답 속도를 경험할 수 있습니다. 또한, Google의 임베딩 모델 대신 한국어 환경에 특화된 오픈소스 임베딩 모델을 사용하여 RAG(검색 증강 생성) 성능을 최적화합니다.

## 🌟 주요 특징

- **🚀 초고속 LLM 추론**: Groq 클라우드의 LPU(Language Processing Unit)를 활용하여 실시간에 가까운 빠른 응답 속도 제공.
- **🔄 유연한 모델 선택**: `llama3-8b-8192`, `mixtral-8x7b-32768` 등 Groq이 제공하는 다양한 최신 오픈소스 LLM을 손쉽게 변경하며 사용 가능.
- **🇰🇷 한국어 특화 RAG**: `jhgan/ko-sbert-nli`와 같은 HuggingFace의 고성능 한국어 임베딩 모델을 사용하여 문서 검색 및 요약의 정확도 향상.
- **🛠️ Google 도구 연동**: 기존 `ai-assist-google`과 동일하게 Gmail, Google Calendar 등 Google Workspace 도구를 활용하는 에이전트 기능 유지.
- **🧩 확장 가능한 아키텍처**: LangChain과 LangGraph를 기반으로 설계되어, 새로운 도구나 전문가 에이전트를 손쉽게 추가할 수 있는 유연한 구조.

## ⚙️ 시스템 아키텍처

![System Architecture](https://i.imgur.com/your-architecture-image.png)
*(여기에 ai-assist-google과 유사한 아키텍처 다이어그램을 삽입할 수 있습니다. LLM과 Embedding 부분이 Groq과 HuggingFace로 변경된 점을 강조하세요.)*

1.  **User Interface**: Streamlit 또는 React/Vue 등 프론트엔드 프레임워크
2.  **Backend (FastAPI)**: 사용자 요청을 받아 처리하는 API 서버
3.  **Agent Executor (LangGraph)**: 사용자의 요청 의도를 파악하고, 적절한 전문가 에이전트(Specialist Agent)나 도구(Tool)를 동적으로 선택하고 실행
4.  **LLM (Groq)**: `ChatGroq`을 통해 Llama 3와 같은 언어 모델을 호출하여 사고(Reasoning)와 응답 생성 담당
5.  **Tools**:
    -   **RAG Retriever**: FAISS 벡터 저장소와 HuggingFace 임베딩을 사용하여 로컬 문서 검색
    -   **Google Tools**: Gmail, Google Calendar API를 사용하여 관련 정보 조회 및 작업 수행
6.  **Vector Store (FAISS)**: HuggingFace 임베딩으로 변환된 문서 벡터를 저장하는 공간

## 🚀 시작하기
