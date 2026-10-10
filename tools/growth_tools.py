import json
import os
from datetime import datetime
from pathlib import Path
from langchain_core.tools import tool

DATA_DIR = Path(__file__).parent.parent / "data"
GROWTH_FILE = DATA_DIR / "growth_records.json"


def _load_records():
    if GROWTH_FILE.exists():
        return json.loads(GROWTH_FILE.read_text(encoding="utf-8"))
    return []


def _save_records(records):
    DATA_DIR.mkdir(exist_ok=True)
    GROWTH_FILE.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")


@tool
def record_growth(
    date: str,
    category: str,
    content: str,
) -> str:
    """记录小朋友的成长点滴。

    Args:
        date: 日期，格式 YYYY-MM-DD，如 2026-10-10
        category: 类别，可选：身高体重、语言发展、运动能力、社交情感、认知学习、其他
        content: 具体内容描述
    """
    record = {
        "date": date,
        "category": category,
        "content": content,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    records = _load_records()
    records.append(record)
    _save_records(records)
    return f"已记录：{date} [{category}] {content}"


@tool
def query_growth(category: str = "", start_date: str = "", end_date: str = "") -> str:
    """查询成长记录。

    Args:
        category: 按类别筛选，可选：身高体重、语言发展、运动能力、社交情感、认知学习、其他。留空查全部
        start_date: 起始日期 YYYY-MM-DD，留空不限制
        end_date: 结束日期 YYYY-MM-DD，留空不限制
    """
    records = _load_records()
    if not records:
        return "还没有任何成长记录。"

    filtered = records
    if category:
        filtered = [r for r in filtered if r["category"] == category]
    if start_date:
        filtered = [r for r in filtered if r["date"] >= start_date]
    if end_date:
        filtered = [r for r in filtered if r["date"] <= end_date]

    if not filtered:
        return "没有找到匹配的记录。"

    lines = [f"[{r['date']}] {r['category']}：{r['content']}" for r in filtered]
    return f"共 {len(filtered)} 条记录：\n" + "\n".join(lines)


@tool
def growth_summary() -> str:
    """生成成长记录统计摘要，包括总记录数、各类别数量、最近记录等。"""
    records = _load_records()
    if not records:
        return "还没有任何成长记录。"

    categories = {}
    for r in records:
        cat = r["category"]
        categories[cat] = categories.get(cat, 0) + 1

    summary = [
        f"总记录数：{len(records)} 条",
        "各类别分布：",
    ]
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        summary.append(f"  - {cat}：{count} 条")

    recent = records[-3:]
    summary.append("\n最近 3 条记录：")
    for r in recent:
        summary.append(f"  [{r['date']}] {r['category']}：{r['content']}")

    return "\n".join(summary)
