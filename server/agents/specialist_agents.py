# server/agents/specialist_agents.py (수정 후)

from langchain_core.tools import tool
from langchain.schema.runnable import RunnablePassthrough
from server.agents.chains import rag_chain
from server.rag.retriever import get_rag_retriever
from server.tools.google_services import get_gmail_service, get_calendar_service
import datetime

@tool("document_search")
def document_search_tool(query: str):
    """
    사용자의 질문과 관련된 로컬 문서를 검색하여 답변을 생성합니다.
    """
    try:
        retriever = get_rag_retriever()

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        rag_runnable = {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        } | rag_chain

        return rag_runnable.invoke(query)
    except Exception as e:
        return f"문서 검색 중 오류가 발생했습니다: {e}"

@tool("gmail_search")
def gmail_search_tool(query: str):
    """
    사용자의 Gmail에서 특정 키워드로 이메일을 검색합니다.
    예: '오늘 온 메일', '김민준에게서 온 메일'
    """
    try:
        service = get_gmail_service()
        results = service.users().messages().list(userId="me", q=query, maxResults=5).execute()
        messages = results.get("messages", [])

        if not messages:
            return "검색된 이메일이 없습니다."

        email_list = []
        for msg in messages:
            txt = service.users().messages().get(userId="me", id=msg["id"]).execute()
            payload = txt["payload"]
            headers = payload.get("headers", [])
            subject = next((d["value"] for d in headers if d["name"] == "Subject"), "제목 없음")
            sender = next((d["value"] for d in headers if d["name"] == "From"), "발신자 불명")
            email_list.append(f"- 보낸이: {sender}, 제목: {subject}")

        return "\n".join(email_list)
    except Exception as e:
        return f"Gmail 검색 중 오류가 발생했습니다. API 인증 상태를 확인해주세요. 오류: {e}"

@tool("calendar_events_lookup")
def calendar_events_lookup_tool(query: str):
    """
    사용자의 Google Calendar에서 오늘 일정을 조회합니다.
    '오늘 일정', '오늘 약속' 등의 키워드에 사용됩니다.
    """
    try:
        service = get_calendar_service()
        # 'Z'는 UTC 시간을 의미합니다.
        now = datetime.datetime.utcnow().isoformat() + "Z"

        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            return "오늘 이후로 예정된 일정이 없습니다."

        event_list = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            # 날짜/시간 형식 파싱 및 가독성 좋은 포맷으로 변환
            try:
                event_time = datetime.datetime.fromisoformat(start.replace("Z", "+00:00"))
                formatted_start = event_time.strftime("%Y-%m-%d %H:%M")
            except ValueError:
                formatted_start = start # 날짜만 있는 경우
            event_list.append(f"- {formatted_start}: {event['summary']}")

        return "\n".join(event_list)
    except Exception as e:
        return f"캘린더 조회 중 오류가 발생했습니다. API 인증 상태를 확인해주세요. 오류: {e}"

available_tools = [
    document_search_tool,
    gmail_search_tool,
    calendar_events_lookup_tool,
]