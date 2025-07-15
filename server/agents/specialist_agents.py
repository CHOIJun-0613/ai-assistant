from langchain_core.tools import tool
from langchain.schema.runnable import RunnablePassthrough
from server.agents.chains import rag_chain
from server.rag.retriever import get_rag_retriever
from server.tools.google_services import get_gmail_service, get_calendar_service
import datetime
# CHANGED: Added DuckDuckGoSearchRun for web search capability
from langchain_community.tools import DuckDuckGoSearchRun

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
    # --- 자연어 쿼리 변환 로직 추가 ---
    def convert_query(natural_query):
        import re
        from datetime import datetime, timedelta

        today = datetime.utcnow().date()
        # 기존 "오늘", "어제" 처리
        if "오늘" in natural_query:
            # 오늘 받은 메일: 오늘 날짜로 검색
            after = today.strftime("%Y/%m/%d")
            return f"after:{after}"
        if "어제" in natural_query:
            # 어제 받은 메일
            yesterday = (today - timedelta(days=1)).strftime("%Y/%m/%d")
            return f"after:{yesterday} before:{today.strftime('%Y/%m/%d')}"
        # "7월12일"과 같은 날짜 패턴 처리 (공백 허용, 오타 수정)
        m = re.search(r"(\d{1,2})\s*월\s*(\d{1,2})\s*일", natural_query)
        if m:
            month = int(m.group(1))
            day = int(m.group(2))
            year = today.year
            try:
                target_date = datetime(year, month, day).date()
                after = target_date.strftime("%Y/%m/%d")
                before = (target_date + timedelta(days=1)).strftime("%Y/%m/%d")
                return f"after:{after} before:{before}"
            except Exception as e:
                print(f"[WARN] 날짜 변환 실패: {e}")
        # 보낸이 검색
        m = re.search(r"(.+)에게서 온 메일", natural_query)
        if m:
            sender = m.group(1)
            return f'from:{sender}'
        # 기본: 원본 쿼리 그대로 사용
        return natural_query

    def extract_body(payload):
        import base64
        import quopri

        def decode_part(part):
            data = part.get("body", {}).get("data")
            if not data:
                return ""
            try:
                decoded_bytes = base64.urlsafe_b64decode(data.encode("UTF-8"))
                try:
                    return decoded_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    return quopri.decodestring(decoded_bytes).decode("utf-8", errors="ignore")
            except Exception:
                return ""
        # multipart
        if "parts" in payload:
            for part in payload["parts"]:
                if part.get("mimeType", "").startswith("text/plain"):
                    return decode_part(part)
            # fallback: first part
            return decode_part(payload["parts"][0])
        # single part
        return decode_part(payload)
    
    def extract_received_time(headers):
        # "Date" 헤더에서 수신 시간 추출
        from email.utils import parsedate_to_datetime
        date_str = next((d["value"] for d in headers if d["name"].lower() == "date"), None)
        if date_str:
            try:
                dt = parsedate_to_datetime(date_str)
                # 한국 시간(KST)로 변환하려면: dt.astimezone(timezone(timedelta(hours=9)))
                return dt.strftime("%Y-%m-%d %H:%M")
            except Exception:
                return date_str
        return "(시간 정보 없음)"
    

    try:
        gmail_query = convert_query(query)
        print(f"[INFO] Gmail Tool: 변환된 쿼리 '{gmail_query}'로 이메일 조회 시작")
        service = get_gmail_service()
        results = service.users().messages().list(userId="me", q=gmail_query, maxResults=5).execute()
        print(f"[INFO] Gmail Tool: 검색 결과 {results}")
        messages = results.get("messages", [])
        
        if not messages:
            return "검색된 이메일이 없습니다."
        
        email_list = []
        for msg in messages:
            txt = service.users().messages().get(userId="me", id=msg["id"], format="full").execute()
            payload = txt["payload"]
            headers = payload["headers"]
            subject = next((d["value"] for d in headers if d["name"] == "Subject"), "(제목 없음)")
            sender = next((d["value"] for d in headers if d["name"] == "From"), "(보낸이 없음)")
            received_time = extract_received_time(headers)
            snippet = txt.get("snippet", "")
            body = extract_body(payload).strip()
            # 본문이 너무 길면 앞부분만 요약
            if body:
                preview = body[:200] + ("..." if len(body) > 200 else "")
            else:
                preview = snippet
            email_list.append(
                f"- 보낸이: {sender}\n  제목: {subject}\n  수신시각: {received_time}\n  내용: {preview}"
            )
            print(f"- 보낸이: {sender}, 제목: {subject}, 수신시각: {received_time}")
        return "\n\n".join(email_list)
    except Exception as e:
        print(f"[ERROR] Gmail Tool: {e}")
        return f"Gmail 조회 중 오류가 발생했습니다. API 인증 상태를 확인해주세요. 오류: {e}"


@tool("calendar_events_lookup")
def calendar_events_lookup_tool(query: str):
    """
    사용자의 Google Calendar에서 지정한 날짜의 일정을 조회합니다.
    예: '오늘 일정', '내일 일정', '7월12일 일정'
    """
    def parse_date_from_query(natural_query):
        import re
        from datetime import datetime, timedelta

        today = datetime.utcnow().date()
        # "오늘"
        if "오늘" in natural_query:
            target_date = today
        # "내일"
        elif "내일" in natural_query:
            target_date = today + timedelta(days=1)
        # "어제"
        elif "어제" in natural_query:
            target_date = today - timedelta(days=1)
        # "7월21일" 패턴
        else:
            m = re.search(r"(\d{1,2})\s*월\s*(\d{1,2})\s*일", natural_query)
            if m:
                month = int(m.group(1))
                day = int(m.group(2))
                year = today.year
                try:
                    candidate = datetime(year, month, day).date()
                    if candidate < today:
                        candidate = datetime(year + 1, month, day).date()
                    target_date = candidate
                except Exception as e:
                    print(f"[WARN] 날짜 변환 실패: {e}")
                    target_date = today
            else:
                target_date = today
        # 시작/끝 시간 (UTC 기준)
        time_min = datetime.combine(target_date, datetime.min.time()).isoformat() + "Z"
        time_max = datetime.combine(target_date, datetime.max.time()).isoformat() + "Z"
        return time_min, time_max, target_date
    try:
        time_min, time_max, target_date = parse_date_from_query(query)
        print(f"[INFO] Calendar Tool: {query} → {time_min} ~ {time_max}")
        service = get_calendar_service()
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=time_min,
                timeMax=time_max,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            return f"{target_date.strftime('%Y-%m-%d')}에 예정된 일정이 없습니다."

        event_list = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            event_list.append(f"- {start}: {event['summary']}")
        return "\n".join(event_list)
    except Exception as e:
        print(f"[ERROR] Calendar Tool: {e}")
        return f"캘린더 조회 중 오류가 발생했습니다. API 인증 상태를 확인해주세요. 오류: {e}"

# --- CHANGED: Added a new web search tool ---
@tool("web_search")
def web_search_tool(query: str):
    """
    'Groq이 뭐야?'와 같이 최신 정보나 일반적인 지식이 필요한 질문에 답하기 위해 웹을 검색합니다.
    로컬 문서에 없을 것 같은 주제에 사용하세요.
    """
    search = DuckDuckGoSearchRun()
    return search.run(query)

# --- CHANGED: Added the new tool to the list of available tools ---
available_tools = [
    document_search_tool,
    gmail_search_tool,
    calendar_events_lookup_tool,
    web_search_tool,
]
