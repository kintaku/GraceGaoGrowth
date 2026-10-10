import json
from datetime import datetime
from pathlib import Path
from langchain_core.tools import tool

DATA_DIR = Path(__file__).parent.parent / "data"
CURRICULUM_FILE = DATA_DIR / "curriculum.json"


def _load_curriculum():
    if CURRICULUM_FILE.exists():
        return json.loads(CURRICULUM_FILE.read_text(encoding="utf-8"))
    return []


def _save_curriculum(items):
    DATA_DIR.mkdir(exist_ok=True)
    CURRICULUM_FILE.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


@tool
def generate_curriculum(
    child_age_months: int,
    interests: str,
    duration_minutes: int = 30,
) -> str:
    """根据小朋友年龄和兴趣生成家庭课程建议。

    Args:
        child_age_months: 小朋友年龄（月龄），如 24 表示 2 岁
        interests: 兴趣爱好，用逗号分隔，如 "画画,音乐,积木"
        duration_minutes: 每次课程时长（分钟），默认 30
    """
    age_years = child_age_months // 12
    age_months = child_age_months % 12

    interest_list = [i.strip() for i in interests.split(",") if i.strip()]

    age_stage = ""
    if child_age_months < 12:
        age_stage = "婴儿期（0-1岁）"
    elif child_age_months < 36:
        age_stage = "幼儿期（1-3岁）"
    elif child_age_months < 72:
        age_stage = "学龄前期（3-6岁）"
    else:
        age_stage = "学龄期（6岁+）"

    activity_suggestions = {
        "画画": ["手指画", "蜡笔涂鸦", "水彩画", "贴纸画"],
        "音乐": ["儿歌跟唱", "节奏拍手", "简单乐器体验", "音乐律动"],
        "积木": ["自由搭建", "按图搭建", "故事场景搭建", "分类整理"],
        "阅读": ["绘本共读", "指认游戏", "故事复述", "角色扮演"],
        "运动": ["平衡练习", "球类游戏", "跳跃游戏", "障碍赛跑"],
        "自然": ["户外观察", "植物种植", "昆虫探索", "天气记录"],
    }

    activities = []
    for interest in interest_list:
        matched = [v for k, v in activity_suggestions.items() if interest in k]
        if matched:
            activities.extend(matched[0][:2])
    if not activities:
        activities = ["自由探索游戏", "亲子互动游戏", "感官体验活动"]

    curriculum = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "age": f"{age_years}岁{age_months}个月",
        "age_stage": age_stage,
        "interests": interest_list,
        "duration": f"{duration_minutes}分钟",
        "activities": activities[:4],
        "tips": f"适合{age_stage}的孩子，建议每次专注一个活动，观察孩子的反应和兴趣点。",
    }

    items = _load_curriculum()
    items.append(curriculum)
    _save_curriculum(items)

    lines = [
        f"家庭课程建议（{curriculum['date']}）",
        f"孩子年龄：{curriculum['age']}（{age_stage}）",
        f"兴趣爱好：{', '.join(interest_list)}",
        f"建议时长：{duration_minutes}分钟",
        "",
        "推荐活动：",
    ]
    for i, act in enumerate(activities[:4], 1):
        lines.append(f"  {i}. {act}")
    lines.append(f"\n小贴士：{curriculum['tips']}")

    return "\n".join(lines)


@tool
def list_curriculum() -> str:
    """查看历史课程建议记录。"""
    items = _load_curriculum()
    if not items:
        return "还没有生成过课程建议。"

    lines = [f"共 {len(items)} 份课程建议："]
    for item in items[-5:]:
        lines.append(f"\n[{item['date']}] {item['age']} - 兴趣：{', '.join(item['interests'])}")
        for act in item["activities"]:
            lines.append(f"  - {act}")
    return "\n".join(lines)
