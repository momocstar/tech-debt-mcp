import sys
import os
import json
from typing import Any, List
from mcp.server import Server
from mcp.types import TextContent, Tool, CallToolResult

from tools.complexity import compute_complexity
from tools.smells import detect_code_smells
from tools.coverage import calculate_coverage
from tools.prioritize import prioritize_debt
from tools.roadmap import generate_roadmap
from tools.sonarqube import get_sonarqube_metrics
from tools.ai_suggestions import generate_refactor_suggestions
from tools.advanced_smells import detect_advanced_smells
from tools.incremental_analyzer import IncrementalAnalyzer
from exporters import OutputFormatter
from dashboard import DashboardGenerator
sys.path.insert(0, os.path.dirname(__file__))

server = Server("tech-debt")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """返回所有可用的工具列表"""
    return [
        Tool(
            name="compute_complexity",
            description="计算项目代码复杂度，支持增量分析",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string", "description": "项目根目录路径"},
                    "max_items": {"type": "integer", "description": "返回的最大项数，默认20"},
                    "since_commit": {"type": "string", "description": "只分析自该commit以来的变更文件，如 HEAD~5"}
                },
                "required": ["project_path"]
            }
        ),
        Tool(
            name="detect_code_smells",
            description="检测代码坏味（长方法、上帝类、重复代码）",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string", "description": "项目根目录路径"},
                    "max_items": {"type": "integer", "description": "返回的最大项数，默认20"}
                },
                "required": ["project_path"]
            }
        ),
        Tool(
            name="calculate_coverage",
            description="解析 JaCoCo XML 报告，返回低覆盖率项",
            inputSchema={
                "type": "object",
                "properties": {
                    "report_path": {"type": "string", "description": "JaCoCo XML 报告路径"},
                    "max_items": {"type": "integer", "description": "返回的最大项数，默认20"}
                },
                "required": ["report_path"]
            }
        ),
        Tool(
            name="prioritize_debt",
            description="对技术债务项进行优先级排序，并可生成AI建议",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string", "description": "项目根目录路径"},
                    "items_json": {"type": "string", "description": "债务项JSON字符串（列表）"},
                    "weights_json": {"type": "string", "description": "权重JSON字符串（可选）"},
                    "business_tags_json": {"type": "string", "description": "业务影响标签JSON（可选）"},
                    "generate_suggestions": {"type": "boolean", "description": "是否生成AI建议"}
                },
                "required": ["project_path", "items_json"]
            }
        ),
        Tool(
            name="generate_roadmap",
            description="根据排序后的债务项生成治理路线图",
            inputSchema={
                "type": "object",
                "properties": {
                    "prioritized_items_json": {"type": "string", "description": "排序后的债务项JSON"},
                    "sprint_capacity": {"type": "integer", "description": "每个Sprint能处理的项目数"},
                    "sprint_days": {"type": "integer", "description": "Sprint天数，默认14"},
                    "start_date": {"type": "string", "description": "开始日期 YYYY-MM-DD"}
                },
                "required": ["prioritized_items_json", "sprint_capacity"]
            }
        ),
        Tool(
            name="get_sonarqube_metrics",
            description="从SonarQube获取度量数据",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_key": {"type": "string", "description": "SonarQube项目键"},
                    "base_url": {"type": "string", "description": "SonarQube服务器URL"},
                    "token": {"type": "string", "description": "访问令牌"}
                },
                "required": ["project_key"]
            }
        ),
        Tool(
            name="generate_refactor_suggestions",
            description="为债务项生成AI重构建议",
            inputSchema={
                "type": "object",
                "properties": {
                    "items_json": {"type": "string", "description": "债务项JSON列表"}
                },
                "required": ["items_json"]
            }
        ),
        Tool(
            name="detect_advanced_smells",
            description="检测高级代码坏味（深层嵌套、魔法数字、长参数列表、数据类、过度注释）",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string", "description": "项目根目录路径"},
                    "max_items": {"type": "integer", "description": "返回的最大项数，默认20"}
                },
                "required": ["project_path"]
            }
        ),
        Tool(
            name="run_incremental_analysis",
            description="运行增量分析（基于上次状态，只分析变更文件）",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string", "description": "项目根目录路径"},
                    "since_commit": {"type": "string", "description": "起始commit，如 HEAD~5"}
                },
                "required": ["project_path"]
            }
        ),
        Tool(
            name="run_full_analysis",
            description="运行全量分析并保存状态",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {"type": "string", "description": "项目根目录路径"}
                },
                "required": ["project_path"]
            }
        ),
        Tool(
            name="format_output",
            description="格式化输出为多种格式（json/markdown/html/csv）",
            inputSchema={
                "type": "object",
                "properties": {
                    "data_json": {"type": "string", "description": "要格式化的数据JSON"},
                    "format": {"type": "string", "description": "输出格式：json, markdown, html, csv", "enum": ["json", "markdown", "html", "csv"]},
                    "title": {"type": "string", "description": "报告标题"}
                },
                "required": ["data_json", "format"]
            }
        ),
        Tool(
            name="generate_dashboard",
            description="生成可视化仪表板HTML报告",
            inputSchema={
                "type": "object",
                "properties": {
                    "data_json": {"type": "string", "description": "债务数据JSON"},
                    "output_path": {"type": "string", "description": "输出文件路径"},
                    "title": {"type": "string", "description": "报告标题"}
                },
                "required": ["data_json", "output_path"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    """处理工具调用"""
    try:
        if name == "compute_complexity":
            result = compute_complexity(
                project_path=arguments["project_path"],
                max_items=arguments.get("max_items", 20),
                since_commit=arguments.get("since_commit")
            )
        elif name == "detect_code_smells":
            result = detect_code_smells(
                project_path=arguments["project_path"],
                max_items=arguments.get("max_items", 20)
            )
        elif name == "calculate_coverage":
            result = calculate_coverage(
                report_path=arguments["report_path"],
                max_items=arguments.get("max_items", 20)
            )
        elif name == "prioritize_debt":
            result = prioritize_debt(
                project_path=arguments["project_path"],
                items=json.loads(arguments["items_json"]),
                weights=json.loads(arguments["weights_json"]) if arguments.get("weights_json") else None,
                business_tags=json.loads(arguments["business_tags_json"]) if arguments.get("business_tags_json") else None,
                generate_suggestions=arguments.get("generate_suggestions", False)
            )
        elif name == "generate_roadmap":
            result = generate_roadmap(
                prioritized_items=json.loads(arguments["prioritized_items_json"]),
                sprint_capacity=arguments["sprint_capacity"],
                sprint_days=arguments.get("sprint_days", 14),
                start_date=arguments.get("start_date")
            )
        elif name == "get_sonarqube_metrics":
            result = get_sonarqube_metrics(
                project_key=arguments["project_key"],
                base_url=arguments.get("base_url"),
                token=arguments.get("token")
            )
        elif name == "generate_refactor_suggestions":
            result = generate_refactor_suggestions(
                items=json.loads(arguments["items_json"])
            )
        elif name == "detect_advanced_smells":
            result = detect_advanced_smells(
                project_path=arguments["project_path"],
                max_items=arguments.get("max_items", 20)
            )
        elif name == "run_incremental_analysis":
            analyzer = IncrementalAnalyzer(arguments["project_path"])
            result = analyzer.analyze_incremental(
                since_commit=arguments.get("since_commit")
            )
        elif name == "run_full_analysis":
            result = IncrementalAnalyzer.run_full_analysis(arguments["project_path"])
        elif name == "format_output":
            data = json.loads(arguments["data_json"])
            format_type = arguments["format"]
            title = arguments.get("title", "技术债务分析报告")

            formatter = OutputFormatter()
            if format_type == "json":
                output = formatter.to_json(data, pretty=True)
            elif format_type == "markdown":
                output = formatter.to_markdown(data, title)
            elif format_type == "html":
                output = formatter.to_html(data, title)
            elif format_type == "csv":
                output = formatter.to_csv(data)
            else:
                return [TextContent(type="text", text=f"不支持的格式: {format_type}")]

            result = {"output": output, "format": format_type}
        elif name == "generate_dashboard":
            data = json.loads(arguments["data_json"])
            output_path = arguments["output_path"]
            title = arguments.get("title", "技术债务分析报告")

            dashboard = DashboardGenerator()
            dashboard.generate_html_report(data, output_path, title)
            result = {
                "output_path": output_path,
                "message": f"可视化仪表板已生成: {output_path}"
            }
        else:
            return [TextContent(type="text", text=f"未知工具: {name}")]

        # 将结果转换为 JSON 字符串并返回
        return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
    except Exception as e:
        return [TextContent(type="text", text=f"执行出错: {str(e)}")]

def run_cli(args):
    """命令行直接调用"""
    import json

    if args.command == "complexity":
        result = compute_complexity(
            project_path=args.project_path,
            max_items=args.max_items,
            since_commit=args.since_commit
        )
    elif args.command == "smells":
        result = detect_code_smells(
            project_path=args.project_path,
            max_items=args.max_items
        )
    elif args.command == "coverage":
        result = calculate_coverage(
            report_path=args.report_path,
            max_items=args.max_items
        )
    elif args.command == "prioritize":
        result = prioritize_debt(
            project_path=args.project_path,
            items=json.loads(args.items_json),
            weights=json.loads(args.weights) if args.weights else None,
            business_tags=json.loads(args.business_tags) if args.business_tags else None,
            generate_suggestions=args.suggestions
        )
    elif args.command == "roadmap":
        result = generate_roadmap(
            prioritized_items=json.loads(args.items_json),
            sprint_capacity=args.capacity,
            sprint_days=args.days,
            start_date=args.start_date
        )
    elif args.command == "sonarqube":
        result = get_sonarqube_metrics(
            project_key=args.project_key,
            base_url=args.base_url,
            token=args.token
        )
    elif args.command == "suggestions":
        result = generate_refactor_suggestions(
            items=json.loads(args.items_json)
        )
    elif args.command == "advanced-smells":
        result = detect_advanced_smells(
            project_path=args.project_path,
            max_items=args.max_items
        )
    elif args.command == "incremental":
        analyzer = IncrementalAnalyzer(args.project_path)
        result = analyzer.analyze_incremental(
            since_commit=args.since_commit
        )
    elif args.command == "full-analysis":
        result = IncrementalAnalyzer.run_full_analysis(args.project_path)
    elif args.command == "format":
        data = json.loads(args.data_json)
        formatter = OutputFormatter()

        if args.format == "json":
            output = formatter.to_json(data, pretty=True)
        elif args.format == "markdown":
            output = formatter.to_markdown(data, args.title)
        elif args.format == "html":
            output = formatter.to_html(data, args.title)
        elif args.format == "csv":
            output = formatter.to_csv(data)
        else:
            output = f"不支持的格式: {args.format}"

        result = {"output": output, "format": args.format}
    elif args.command == "dashboard":
        data = json.loads(args.data_json)
        dashboard = DashboardGenerator()
        dashboard.generate_html_report(data, args.output_path, args.title)
        result = {
            "output_path": args.output_path,
            "message": f"可视化仪表板已生成: {args.output_path}"
        }
    else:
        result = {"error": f"未知命令: {args.command}"}

    print(json.dumps(result, indent=2, ensure_ascii=False))

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Tech-Debt-MCP 命令行工具")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # complexity 命令
    p_complexity = subparsers.add_parser("complexity", help="计算代码复杂度")
    p_complexity.add_argument("project_path", help="项目路径")
    p_complexity.add_argument("--max-items", type=int, default=20, help="最大返回项数")
    p_complexity.add_argument("--since-commit", help="只分析该commit后的变更")

    # smells 命令
    p_smells = subparsers.add_parser("smells", help="检测代码坏味")
    p_smells.add_argument("project_path", help="项目路径")
    p_smells.add_argument("--max-items", type=int, default=20, help="最大返回项数")

    # coverage 命令
    p_coverage = subparsers.add_parser("coverage", help="分析测试覆盖率")
    p_coverage.add_argument("report_path", help="JaCoCo XML报告路径")
    p_coverage.add_argument("--max-items", type=int, default=20, help="最大返回项数")

    # prioritize 命令
    p_prioritize = subparsers.add_parser("prioritize", help="债务优先级排序")
    p_prioritize.add_argument("project_path", help="项目路径")
    p_prioritize.add_argument("--items-json", required=True, help="债务项JSON")
    p_prioritize.add_argument("--weights", help="权重JSON")
    p_prioritize.add_argument("--business-tags", help="业务标签JSON")
    p_prioritize.add_argument("--suggestions", action="store_true", help="生成AI建议")

    # roadmap 命令
    p_roadmap = subparsers.add_parser("roadmap", help="生成治理路线图")
    p_roadmap.add_argument("--items-json", required=True, help="排序后债务项JSON")
    p_roadmap.add_argument("--capacity", type=int, required=True, help="每Sprint处理数")
    p_roadmap.add_argument("--days", type=int, default=14, help="Sprint天数")
    p_roadmap.add_argument("--start-date", help="开始日期 YYYY-MM-DD")

    # sonarqube 命令
    p_sonar = subparsers.add_parser("sonarqube", help="从SonarQube获取数据")
    p_sonar.add_argument("project_key", help="项目键")
    p_sonar.add_argument("--base-url", help="SonarQube URL")
    p_sonar.add_argument("--token", help="访问令牌")

    # suggestions 命令
    p_suggest = subparsers.add_parser("suggestions", help="生成AI重构建议")
    p_suggest.add_argument("--items-json", required=True, help="债务项JSON")

    # advanced-smells 命令
    p_advanced = subparsers.add_parser("advanced-smells", help="检测高级代码坏味")
    p_advanced.add_argument("project_path", help="项目路径")
    p_advanced.add_argument("--max-items", type=int, default=20, help="最大返回项数")

    # incremental 命令
    p_incremental = subparsers.add_parser("incremental", help="运行增量分析")
    p_incremental.add_argument("project_path", help="项目路径")
    p_incremental.add_argument("--since-commit", help="起始commit，如 HEAD~5")

    # full-analysis 命令
    p_full = subparsers.add_parser("full-analysis", help="运行全量分析")
    p_full.add_argument("project_path", help="项目路径")

    # format 命令
    p_format = subparsers.add_parser("format", help="格式化输出")
    p_format.add_argument("--data-json", required=True, help="数据JSON")
    p_format.add_argument("--format", required=True, choices=["json", "markdown", "html", "csv"], help="输出格式")
    p_format.add_argument("--title", default="技术债务分析报告", help="报告标题")

    # dashboard 命令
    p_dashboard = subparsers.add_parser("dashboard", help="生成可视化仪表板")
    p_dashboard.add_argument("--data-json", required=True, help="债务数据JSON")
    p_dashboard.add_argument("--output-path", required=True, help="输出文件路径")
    p_dashboard.add_argument("--title", default="技术债务分析报告", help="报告标题")

    args = parser.parse_args()

    if args.command:
        run_cli(args)
    else:
        # 无参数时启动 MCP server
        import asyncio
        from mcp.server.stdio import stdio_server
        from mcp.server import InitializationOptions
        from mcp.types import ServerCapabilities, ToolsCapability

        async def run_mcp():
            async with stdio_server() as (read_stream, write_stream):
                init_options = InitializationOptions(
                    server_name="tech-debt",
                    server_version="1.0.0",
                    capabilities=ServerCapabilities(tools=ToolsCapability())
                )
                await server.run(read_stream, write_stream, init_options)

        asyncio.run(run_mcp())

if __name__ == "__main__":
    main()