from typing import Literal
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from config import MODEL_NAME, TEMPERATURE, NUM_CTX, SYSTEM_PROMPT
from tools.base_tools import get_all_tools


class AgentState(dict):
    messages: list


def build_agent():
    tools = get_all_tools()
    tool_node = ToolNode(tools)

    llm = ChatOllama(
        model=MODEL_NAME,
        temperature=TEMPERATURE,
        num_ctx=NUM_CTX,
    )
    llm_with_tools = llm.bind_tools(tools)

    def should_continue(state) -> Literal["tools", END]:
        messages = state["messages"]
        last_message = messages[-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END

    def call_model(state):
        messages = state["messages"]
        has_system = any(
            (isinstance(m, dict) and m.get("role") == "system") or
            (hasattr(m, "type") and m.type == "system")
            for m in messages
        )
        if not has_system:
            messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)

    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue)
    workflow.add_edge("tools", "agent")

    return workflow.compile()
