"""
Tech-Debt-MCP 使用示例
展示如何使用各个功能模块
"""

# 示例 1: 基本使用

from tools.complexity import compute_complexity
from tools.smells import detect_code_smells
from tools.prioritize import prioritize_debt
from tools.roadmap import generate_roadmap

# 分析项目
project_path = "/path/to/your/project"

# 1. 计算复杂度
print("计算代码复杂度...")
complexity_result = compute_complexity(project_path, max_items=20)
print(f"发现 {len(complexity_result['items'])} 个高复杂度方法")

# 2. 检测代码坏味
print("\n检测代码坏味...")
smells_result = detect_code_smells(project_path, max_items=20)
print(f"发现 {len(smells_result['items'])} 个代码坏味问题")

# 3. 优先级排序
print("\n计算债务优先级...")
all_items = complexity_result['items'] + smells_result['items']

prioritized = prioritize_debt(
    project_path=project_path,
    items=all_items,
    generate_suggestions=False
)
print(f"Top 3 债务项:")
for item in prioritized['items'][:3]:
    print(f"  - {item['entity_name']}: 债务指数 {item['debt_score']:.2f}")

# 4. 生成路线图
print("\n生成治理路线图...")
roadmap = generate_roadmap(
    prioritized_items=prioritized['items'],
    sprint_capacity=5,
    sprint_days=14,
    start_date="2026-04-01"
)

print("\n路线图包含 {len(roadmap['sprints'])} 个 Sprint")


# 示例 2: 使用进度反馈

def progress_callback(current, total, message):
    """进度回调函数"""
    percent = (current / total) * 100
    print(f"[{percent:.0f}%] {message}")

# 带进度的复杂度分析
result = compute_complexity(
    project_path,
    max_items=20,
    progress_callback=progress_callback
)

# 示例 3: 自定义配置

import os

# 设置环境变量
os.environ['COMPLEXITY_THRESHOLD'] = '15'
os.environ['LONG_METHOD_LINES'] = '60'
os.environ['WEIGHT_COMPLEXITY'] = '0.5'

# 运行分析
from config import get_config

config = get_config()
print(f"复杂度阈值: {config.get('COMPLEXITY_THRESHOLD')}")
print(f"长方法阈值: {config.get('LONG_METHOD_LINES')}")
print(f"复杂度权重: {config.get('WEIGHT_COMPLEXITY')}")

# 示例 4: 错误处理

from validation import validate_setup, ErrorHandler

# 验证环境
result = validate_setup()
if not result.is_valid:
    print("环境验证通过")
else:
    print("环境验证失败:")
    for error in result.errors:
        print(f"  错误: {error}")

# 使用错误处理器
try:
    # 尝试分析不存在的项目
    compute_complexity("/nonexistent/path")
except Exception as e:
    error_info = ErrorHandler.project_not_found("/nonexistent/path")
    print(f"错误: {error_info['error']}")
    print(f"建议: {error_info['suggestion']}")

# 示例 5: 输出格式化

from exporters import OutputFormatter
import json

# 准备数据
sample_data = {
    "items": [
        {
            "type": "complex_method",
            "file_path": "/src/Service.java",
            "entity_name": "ComplexMethod",
            "complexity": 25,
            "debt_score": 0.85,
            "modification_frequency": 10
        }
    ]
}

# 导出为不同格式
print("JSON 格式:")
print(OutputFormatter.to_json(sample_data))

print("\nMarkdown 格式:")
print(OutputFormatter.to_markdown(sample_data, "技术债务报告"))

print("\nCSV 格式:")
print(OutputFormatter.to_csv(sample_data))

print("\nHTML 格式:")
print(OutputFormatter.to_html(sample_data, "技术债务报告"))

# 示例 6: 可视化仪表板

from dashboard import DashboardGenerator

# 准备数据
sample_data = {
    "items": [
        {
            "type": "complex_method",
            "file_path": "/src/Service.java",
            "entity_name": "processData",
            "complexity": 25,
            "debt_score": 0.85,
            "modification_frequency": 10
        },
        {
            "type": "long_method",
            "file_path": "/src/Helper.java",
            "entity_name": "validateInput",
            "complexity": 18,
            "debt_score": 0.72,
            "modification_frequency": 5
        }
    ]
}

# 生成仪表板
dashboard = DashboardGenerator(sample_data, "示例仪表板")
print(f"仪表板文件: {dashboard}")

# 实际使用：查看 dashboard.html 文件