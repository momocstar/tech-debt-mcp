from datetime import datetime, timedelta

def generate_roadmap(prioritized_items: list, sprint_capacity: int, sprint_days: int = 14, start_date: str = None) -> dict:
    """
    prioritized_items: 排序后的债务项列表（已包含债务指数）
    sprint_capacity: 每个 sprint 能重构的类/方法数量
    sprint_days: sprint 天数
    start_date: 开始日期，格式 "YYYY-MM-DD"
    """
    if start_date is None:
        start_date = datetime.now().strftime("%Y-%m-%d")
    start = datetime.strptime(start_date, "%Y-%m-%d")
    sprints = []
    remaining = prioritized_items[:]
    sprint_num = 1
    while remaining:
        sprint_items = remaining[:sprint_capacity]
        remaining = remaining[sprint_capacity:]
        sprint_end = start + timedelta(days=sprint_days)
        sprints.append({
            "name": f"Sprint {sprint_num}",
            "start": start.strftime("%Y-%m-%d"),
            "end": sprint_end.strftime("%Y-%m-%d"),
            "items": sprint_items
        })
        sprint_num += 1
        start = sprint_end
    return {"sprints": sprints}