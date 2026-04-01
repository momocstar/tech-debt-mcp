# tools/prioritize.py (修改)
from models import DebtItem
from analyzers.git_analyzer import get_modification_frequency
import os
from .ai_suggestions import generate_refactor_suggestions

def prioritize_debt(project_path: str, items: list, weights: dict = None,
                    business_tags: dict = None, generate_suggestions: bool = False) -> dict:
    if weights is None:
        weights = {"complexity": 0.4, "coverage": 0.3, "business": 0.2, "frequency": 0.1}
    debt_items = [DebtItem(**item) for item in items]

    # 获取 Git 修改频率
    try:
        freq_map = get_modification_frequency(project_path)
        for item in debt_items:
            item.modification_frequency = freq_map.get(item.file_path, 0)
    except:
        pass

    # 设置业务影响
    if business_tags:
        for item in debt_items:
            item.business_impact = business_tags.get(item.file_path, item.business_impact)

    for item in debt_items:
        item.debt_score = item.debt_index(weights)
    debt_items.sort(key=lambda x: x.debt_score, reverse=True)

    result = {
        "items": [item.__dict__ for item in debt_items],
        "total": len(debt_items)
    }

    if generate_suggestions:
        # 只对 top 10 生成建议
        top_items = result["items"][:10]
        suggestions = generate_refactor_suggestions(top_items)
        result["suggestions"] = suggestions

    return result