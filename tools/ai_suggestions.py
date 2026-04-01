# tools/ai_suggestions.py
import os
import json
import requests
from typing import List, Dict
from models import DebtItem

def generate_refactor_suggestions(items: List[Dict], api_key: str = None, model: str = "claude-3-sonnet-20240229") -> List[Dict]:
    """
    调用 Claude API 为每个债务项生成重构建议。
    items: 债务项列表（每个是 DebtItem 的 dict）
    api_key: 从环境变量 ANTHROPIC_API_KEY 读取
    """
    if not api_key:
        api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        # 返回模拟建议
        return _mock_suggestions(items)

    suggestions = []
    for item in items:
        # 构建 prompt
        prompt = f"""请为以下技术债务项提供具体的重构建议：

- 文件: {item['file_path']}
- 实体: {item['entity_name']}
- 类型: {item['type']}
- 复杂度: {item.get('complexity', 'N/A')}
- 覆盖率: {item.get('coverage', 'N/A')}
- 修改频率: {item.get('modification_frequency', 'N/A')}

请给出简洁、可操作的重构步骤，例如提取方法、拆分接口、增加测试等。输出格式为纯文本，不要使用markdown。"""
        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": model,
                    "max_tokens": 300,
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            if response.status_code == 200:
                suggestion = response.json()['content'][0]['text']
            else:
                suggestion = "无法生成建议，请检查API配置。"
        except Exception as e:
            suggestion = f"生成建议失败: {str(e)}"
        suggestions.append({
            "id": item['id'],
            "suggestion": suggestion
        })
    return suggestions

def _mock_suggestions(items: List[Dict]) -> List[Dict]:
    """当无API key时返回模拟建议"""
    suggestions = []
    for item in items:
        if item['type'] == 'complex_method':
            sug = "建议将该方法拆分为多个小方法，每个方法只做一件事。"
        elif item['type'] == 'god_class':
            sug = "按职责拆分：提取相关方法到新类中，遵循单一职责原则。"
        elif item['type'] == 'low_coverage':
            sug = "先为现有代码编写单元测试，再逐步重构。"
        else:
            sug = "请分析代码并应用合适的重构模式。"
        suggestions.append({"id": item['id'], "suggestion": sug})
    return suggestions