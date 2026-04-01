import xml.etree.ElementTree as ET
import os
from models import DebtItem, DebtType

def calculate_coverage(report_path: str, max_items: int = 20) -> dict:
    """解析 JaCoCo XML 报告，返回低覆盖率项"""
    items = []
    if not os.path.exists(report_path):
        return {"error": f"Report not found: {report_path}", "items": []}
    tree = ET.parse(report_path)
    root = tree.getroot()
    # 查找 package/class 节点
    for package in root.findall('package'):
        for clazz in package.findall('class'):
            class_name = clazz.get('name')
            counter = clazz.find("counter[@type='INSTRUCTION']")
            if counter is not None:
                missed = int(counter.get('missed', 0))
                covered = int(counter.get('covered', 0))
                total = missed + covered
                coverage = covered / total if total > 0 else 0
                if coverage < 0.7:  # 低于70%覆盖率
                    items.append(DebtItem(
                        id=class_name,
                        type=DebtType.LOW_COVERAGE,
                        file_path=class_name.replace('.', '/') + '.java',
                        entity_name=class_name,
                        coverage=coverage
                    ))
    items.sort(key=lambda x: x.coverage or 1)
    truncated = len(items) > max_items
    if truncated:
        items = items[:max_items]
    return {
        "items": [item.__dict__ for item in items],
        "total_count": len(items) if not truncated else "more than " + str(max_items),
        "truncated": truncated
    }