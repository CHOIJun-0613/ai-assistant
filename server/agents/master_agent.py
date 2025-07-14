# server/agents/master_agent.py (수정 후)

from langchain.tools.render import render_text_description
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.json import JsonOutputParser
from server.agents.specialist_agents import available_tools
from server.agents.chains import general_chain, llm

def get_master_agent_runnable():
    """
    사용자의 질문을 분석하여 가장 적합한 도구를 선택하거나,
    일반 대화로 처리하는 마스터 에이전트의 실행 체인을 생성합니다.
    """
    rendered_tools = render_text_description(available_tools)

    prompt_template = ChatPromptTemplate.from_template(
        """
        You are an AI agent responsible for analyzing user requests and selecting the most appropriate tool.
        Choose one of the available tools that best fits the given question and return it in JSON format with the arguments to pass to the tool.
        If no suitable tool is found, select "general_conversation".

        Available Tools:
        {tools}

        User Question:
        {input}

        Output Format (JSON):
        {{
          "tool_name": "Selected tool name",
          "tool_input": "Value to pass to the tool"
        }}
        """
    )

    return prompt_template | llm | JsonOutputParser()

def route_request(state: dict) -> dict:
    """
    LangGraph의 라우팅 노드. 마스터 에이전트를 실행하여 다음 단계를 결정합니다.
    """
    master_agent = get_master_agent_runnable()

    try:
        result = master_agent.invoke({"input": state["query"], "tools": render_text_description(available_tools)})
        tool_name = result.get("tool_name")
        tool_input = result.get("tool_input")

        # --- 개선: 동적으로 도구를 찾아 실행하여 확장성 확보 ---
        if tool_name and tool_name != "general_conversation":
            for tool in available_tools:
                if tool.name == tool_name:
                    response = tool.invoke(tool_input)
                    return {"response": response}
        # --- 개선 끝 ---

        # 적절한 도구가 없으면 일반 대화 체인 실행
        response = general_chain.invoke({"question": state["query"], "history": state["history"]})
        return {"response": response}

    except Exception as e:
        # 마스터 에이전트 실패 시 예외 처리 및 일반 대화로 폴백
        print(f"마스터 에이전트 실행 중 오류 발생: {e}")
        response = general_chain.invoke({"question": state["query"], "history": state["history"]})
        return {"response": response}