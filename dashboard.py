"""
Tech-Debt-MCP 可视化仪表板生成器
生成 HTML 可视化报告，包含图表和统计信息
"""
import json
from datetime import datetime
from typing import Dict, List
import os


class DashboardGenerator:
    """仪表板生成器"""

    @staticmethod
    def generate_html_report(data: Dict, output_path: str, title: str = "技术债务分析报告") -> str:
        """
        生成 HTML 仪表板报告

        Args:
            data: 债务数据
            output_path: 输出文件路径
            title: 报告标题
        """
        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: #f5f5f5;
            color: #333;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            margin-bottom: 20px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-card h3 {{
            margin: 0;
            color: #666;
            font-size: 14px;
        }}
        .stat-card p {{
            font-size: 32px;
            font-weight: bold;
            color: #333;
            margin: 10px 0 0;
        }}
        .chart-container {{
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .chart-container h2 {{
            color: #2c3e50;
            margin-bottom: 15px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 2px solid #ddd;
        }}
        th {{
            background-color: #f5f5f5;
            color: #333;
            font-weight: bold;
        }}
        tr:hover {{
            background-color: #f9f9f9;
        }}
        .priority-high {{
            background-color: #fee;
        }}
        .priority-medium {{
            background-color: #fff9e6;
        }}
        .priority-low {{
            background-color: #e8f5e8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>

        <div class="stats-grid">
            <div class="stat-card">
                <h3>总债务项</h3>
                <p id="total-items">{0}</p>
            </div>

            <div class="stat-card">
                <h3>高优先级</h3>
                <p id="high-priority">0</p>
            </div>

            <div class="stat-card">
                <h3>平均复杂度</h3>
                <p id="avg-complexity">0</p>
            </div>

            <div class="stat-card">
                <h3>总修改次数</h3>
                <p id="total-modifications">0</p>
            </div>
        </div>

        <div class="chart-container">
            <h2>债务分布（按类型）</h2>
            <canvas id="typeChart" style="height: 300px;"></canvas>
        </div>

        <div class="chart-container">
            <h2>复杂度分布</h2>
            <canvas id="complexityChart" style="height: 300px;"></canvas>
        </div>

        <div class="chart-container">
            <h2>Top 10 债务项</h2>
            <table>
                <thead>
                    <tr>
                        <th>序号</th>
                        <th>类型</th>
                        <th>文件</th>
                        <th>实体</th>
                        <th>复杂度</th>
                        <th>债务指数</th>
                        <th>优先级</th>
                    </tr>
                </thead>
                <tbody id="debt-table">
                </tbody>
            </table>
        </div>
    </div>

    <script>
        // 数据处理
        const items = {items};
        const totalItems = items.length;
        const highPriority = items.filter(i => i.debt_score >= 0.5).length;
        const avgComplexity = items.reduce((sum, i) => sum + i.complexity, 0) / items.length;
        const totalModifications = items.reduce((sum, i) => sum + i.modification_frequency || 0, 0);

        // 更新统计数据
        document.getElementById('total-items').textContent = totalItems;
        document.getElementById('high-priority').textContent = highPriority;
        document.getElementById('avg-complexity').textContent = avgComplexity.toFixed(1);
        document.getElementById('total-modifications').textContent = totalModifications;

        // 类型分布图表
        const typeCtx = document.getElementById('typeChart').getContext('2d');
        const typeChart = new Chart(typeCtx, {
            type: 'doughnut',
            data: Object.entries(
                items.reduce((acc, item) => {
                    acc[item.type] = (acc[item.type] || 0) + 1;
                    return acc;
                }, {})
            ),
            options: {{
                responsive: true,
                plugins: {{
                    legend: {
                        position: 'right',
                        labels: Object.keys(items.reduce((acc, item) => {
                            acc[item.type] = (acc[item.type] || 'Unknown');
                            return label;
                        }, {}))
                    }
                }
            }
        });

        // 复杂度分布图表
        const complexityCtx = document.getElementById('complexityChart').getContext('2d');
        const complexityChart = new Chart(complexityCtx, {
            type: 'bar',
            data: items.slice(0, 10).map((item, index) => ({
                x: index,
                y: item.complexity || 0,
                label: item.entity_name
            })),
            options: {
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true
                    }
                }
            }
        });

        // 巻加表格行
        const tbody = document.getElementById('debt-table');
        items.slice(0, 10).forEach((item, index) => {
            const priority = item.debt_score >= 0.5 ? 'high' : item.debt_score >= 0.3 ? 'medium' : 'low';
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>{index + 1}</td>
                <td>${item.type}</td>
                <td title="${item.file_path}">${item.file_path.split('/').pop()}</td>
                <td>${item.entity_name}</td>
                <td>${item.complexity}</td>
                <td>${item.debt_score.toFixed(2)}</td>
                <td class="priority-${priority}">${priority}</td>
            `;
            tbody.appendChild(row);
        });
    </script>
</body>
</html>
"""

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✅ HTML 仪表板已生成: {output_path}")


if __name__ == "__main__":
    import sys

    from pathlib import Path

    # 示例数据
    sample_data = {
        "items": [
            {
                "type': 'complex_method',
                'file_path': '/path/to/File1.java',
                'entity_name': 'ComplexMethod',
                'complexity': 25,
                'debt_score': 0.85,
                'modification_frequency': 10
            },
            {
                'type': 'long_method',
                'file_path': '/path/to/File2.py',
                'entity_name': 'LongMethod',
                'complexity': 15,
                'debt_score': 0.72,
                'modification_frequency': 8
            }
        ]
    }

    output_path = 'dashboard.html'
    DashboardGenerator.generate_html_report(sample_data, output_path, "示例技术债务报告")