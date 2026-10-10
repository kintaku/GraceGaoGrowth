from agent.graph import build_agent


def run_agent():
    app = build_agent()

    print("=" * 50)
    print("家庭成长助手已启动")
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

        for event in app.stream({"messages": messages}):
            for node_name, node_output in event.items():
                if node_name == "agent":
                    msg = node_output["messages"][-1]
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        tool_names = [t["name"] for t in msg.tool_calls]
                        print(f"\n[调用工具: {', '.join(tool_names)}]")
                    else:
                        print(f"\n助手: {msg.content}")
                elif node_name == "tools":
                    for msg in node_output["messages"]:
                        print(f"[工具返回: {msg.content}]")

            messages = node_output["messages"]


if __name__ == "__main__":
    run_agent()
