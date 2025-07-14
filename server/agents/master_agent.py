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
        당신은 사용자의 요청을 분석하여 가장 적절한 도구를 선택하는 역할을 맡은 AI 에이전트입니다.
        주어진 질문에 가장 적합한 도구 하나를 선택하고, 그 도구에 전달할 인자를 JSON 형식으로 반환해야 합니다.
        만약 적절한 도구가 없다면, "일반 대화"를 선택하세요.

        사용 가능한 도구 목록:
        {tools}

        사용자 질문:
        {input}

        출력 형식 (JSON):
        {{
          "tool_name": "선택한 도구 이름",
          "tool_input": "도구에 전달할 값"
        }}
        """
    )
    
    master_agent_chain = prompt_template | llm | JsonOutputParser()
    
    return master_agent_chain

def route_request(state):
    """
    LangGraph의 라우팅 노드. 마스터 에이전트를 실행하여 다음 단계를 결정합니다.
    """
    master_agent = get_master_agent_runnable()
    
    result = master_agent.invoke({"input": state["query"], "tools": render_text_description(available_tools)})
    
    tool_name = result.get("tool_name")
    tool_input = result.get("tool_input")
    
    for tool in available_tools:
        if tool.name == tool_name:
            response = tool.invoke(tool_input)
            return {"response": response}
            
    response = general_chain.invoke({"question": state["query"], "history": state["history"]})
    return {"response": response}
