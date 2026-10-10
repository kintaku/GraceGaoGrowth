from typing import Annotated, Literal, TypedDict
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode


# --- 状态定义 ---
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


# --- 工具定义 ---
@tool
def calculator(expression: str) -> str:
    """计算数学表达式。支持加减乘除、幂运算等。例如: calculator("2 + 3 * 4")"""
    try:
        allowed = set("0123456789+-*/.() ")
        if not all(c in allowed for c in expression):
            return "错误：表达式包含非法字符"
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"计算错误：{e}"


@tool
def get_weather(city: str) -> str:
    """查询城市天气（模拟数据）。"""
    weather_data = {
        "北京": "晴，15°C",
        "上海": "多云，20°C",
        "深圳": "小雨，25°C",
        "杭州": "阴，18°C",
    }
    return weather_data.get(city, f"未找到 {city} 的天气信息，请确认城市名称。")


tools = [calculator, get_weather]
tool_node = ToolNode(tools)


# --- 模型初始化 ---
llm = ChatOllama(
    model="qwen2.5:7b",
    temperature=0.7,
    num_ctx=8192,
)
llm_with_tools = llm.bind_tools(tools)


# --- 节点函数 ---
def should_continue(state: AgentState) -> Literal["tools", END]:
    messages = state["messages"]
    last_message = messages[-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END


def call_model(state: AgentState):
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


# --- 构建图 ---
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")

app = workflow.compile()


# --- 运行 ---
def run_agent():
    print("=" * 50)
    print("Qwen2.5-7B LangGraph Agent 已启动")
    print("可用工具：calculator（计算器）、get_weather（天气查询）")
    print("输入 'exit' 退出")
    print("=" * 50)

    messages = []
    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n再见！")
            break

        if not user_input or user_input.lower() == "exit":
            print("再见！")
            break

        messages.append({"role": "user", "content": user_input})

        final_state = None
        for event in app.stream({"messages": messages}):
            for node_name, node_output in event.items():
                if node_name == "agent":
                    msg = node_output["messages"][-1]
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        tool_names = [t["name"] for t in msg.tool_calls]
                        print(f"\n[Agent 调用工具: {', '.join(tool_names)}]")
                    else:
                        print(f"\nQwen: {msg.content}")
                elif node_name == "tools":
                    for msg in node_output["messages"]:
                        print(f"[工具返回: {msg.content}]")

            final_state = node_output

        if final_state:
            messages = final_state["messages"]


if __name__ == "__main__":
    run_agent()
