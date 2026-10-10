from langchain_core.tools import tool


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


def get_all_tools():
    from tools.growth_tools import record_growth, query_growth, growth_summary
    from tools.curriculum_tools import generate_curriculum, list_curriculum

    return [
        calculator,
        get_weather,
        record_growth,
        query_growth,
        growth_summary,
        generate_curriculum,
        list_curriculum,
    ]
