import streamlit as st
import requests
import json
import sys

# FastAPI 백엔드 서버의 주소
BACKEND_URL = "http://127.0.0.1:8000/api/chat"

# Streamlit 페이지 설정
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="auto",
)

st.title("🤖 AI Assistant (Groq Edition)")
st.caption("Groq의 초고속 LLM과 RAG, Google Tools를 활용하는 AI 업무 비서입니다.")

# 세션 상태에 대화 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "안녕하세요! 무엇을 도와드릴까요? 문서 검색, 메일 확인, 일정 조회 등 다양한 작업을 요청할 수 있습니다."}
    ]

# 이전 대화 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Streamlit 버전 체크
st.write(f"Streamlit version: {st.__version__}")
if tuple(map(int, st.__version__.split("."))) < (1, 25, 0):
    st.error("st.chat_input은 Streamlit 1.25.0 이상에서만 지원됩니다. Streamlit을 업그레이드 해주세요.")

# 사용자 입력 처리
if prompt := st.chat_input("메시지를 입력하세요..."):
    st.write(f"[DEBUG] 사용자 입력: {prompt}")  # 디버깅용 출력
    # 사용자 메시지를 대화 기록에 추가하고 화면에 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 응답을 위해 백엔드에 요청
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        try:
            # 이전 대화 기록을 추출 (API 형식에 맞게)
            history = [msg["content"] for msg in st.session_state.messages[:-1]]
            st.write(f"[DEBUG] 백엔드로 전송: {BACKEND_URL}, 데이터: {{'query': prompt, 'history': history}}")
            # 백엔드 API 호출
            response = requests.post(
                BACKEND_URL,
                headers={"Content-Type": "application/json"},
                data=json.dumps({"query": prompt, "history": history})
            )
            st.write(f"[DEBUG] 백엔드 응답 코드: {response.status_code}")
            response.raise_for_status()  # HTTP 오류 발생 시 예외 처리
            
            # 응답 받은 내용을 화면에 표시
            full_response = response.json().get("response", "오류가 발생했습니다.")
            message_placeholder.markdown(full_response)
            
            # AI 응답을 대화 기록에 추가
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except requests.exceptions.RequestException as e:
            error_message = f"백엔드 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.\n\n오류: {e}"
            message_placeholder.error(error_message)
            st.session_state.messages.append({"role": "assistant", "content": error_message})

# --- 사이드바 ---
with st.sidebar:
    st.header("사용 가이드")
    st.markdown("""
    - **문서 검색**: `프로젝트 A 보고서 요약해줘`
    - **메일 확인**: `어제 온 메일 목록 보여줘`
    - **일정 조회**: `오늘 내 일정 알려줘`
    - **일반 대화**: `Groq이 뭐야?`
    """)
    
    if st.button("대화 기록 초기화"):
        st.session_state.messages = [
            {"role": "assistant", "content": "안녕하세요! 무엇을 도와드릴까요?"}
        ]
        st.rerun()

