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
    retriever = get_rag_retriever()
    
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_runnable = {
        "context": retriever | format_docs,
        "question": RunnablePassthrough(),
    } | rag_chain

    return rag_runnable.invoke(query)

@tool("gmail_search")
def gmail_search_tool(query: str):
    """
    사용자의 Gmail에서 특정 키워드로 이메일을 검색합니다.
    예: '오늘 온 메일', '김민준에게서 온 메일'
    """
    service = get_gmail_service()
    results = service.users().messages().list(userId="me", q=query, maxResults=5).execute()
    messages = results.get("messages", [])
    
    if not messages:
        return "검색된 이메일이 없습니다."
    
    email_list = []
    for msg in messages:
        txt = service.users().messages().get(userId="me", id=msg["id"]).execute()
        payload = txt["payload"]
        headers = payload["headers"]
        subject = next(d["value"] for d in headers if d["name"] == "Subject")
        sender = next(d["value"] for d in headers if d["name"] == "From")
        email_list.append(f"- 보낸이: {sender}, 제목: {subject}")
        
    return "\n".join(email_list)

@tool("calendar_events_lookup")
def calendar_events_lookup_tool(query: str):
    """
    사용자의 Google Calendar에서 오늘 일정을 조회합니다.
    '오늘 일정', '오늘 약속' 등의 키워드에 사용됩니다.
    """
    service = get_calendar_service()
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
        return "오늘 예정된 일정이 없습니다."

    event_list = []
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        event_list.append(f"- {start}: {event['summary']}")
        
    return "\n".join(event_list)

available_tools = [
    document_search_tool,
    gmail_search_tool,
    calendar_events_lookup_tool,
]
