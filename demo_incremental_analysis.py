#!/usr/bin/env python3
"""
增量分析演示脚本
展示如何使用增量分析功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.incremental_analyzer import IncrementalAnalyzer, run_full_analysis


def main():
    print("=" * 80)
    print("增量分析演示")
    print("=" * 80)

    # 使用 Intelligent-health-service 项目
    project_path = '/Users/momoc/Desktop/xs/Intelligent-health-service'

    if not os.path.exists(project_path):
        print(f"错误: 项目路径不存在: {project_path}")
        sys.exit(1)

    # 创建分析器
    analyzer = IncrementalAnalyzer(project_path)
    try:
        # 1. 全量分析
        print("\n1. 运行全量分析...")
        full_result = run_full_analysis(project_path)

        print(f"\n全量分析结果:")
        print(f"  总债务项: {full_result['total_count']}")
        if full_result.get('items'):
            print(f"  前 5 项:")
            for i, item in enumerate(full_result['items'][:5], 1):
                print(f"  {i}. {item.get('entity_name', 'N/A')} - 复杂度: {item.get('complexity', 'N/A')}")

        # 2. 声量分析（HEAD~5)
        print("\n2. 运行增量分析（HEAD~5)...")
        incremental_result = analyzer.analyze_incremental(since_commit='HEAD~5')

        if incremental_result.get('error'):
            print(f"\n  错误: {incremental_result['error']}")
            print(f"  建议: {incremental_result.get('suggestion', '')}")
        else:
            print(f"\n增量分析结果:")
            print(f"  变更文件: {len(incremental_result.get('changed_files', []))}")
            print(f"  新增债务: {incremental_result.get('total_count', 0)}")
            if incremental_result.get('items'):
                print(f"\n  新增债务项:")
                for i, item in enumerate(incremental_result['items'][:5], 1):
                    print(f"  {i}. {item.get('entity_name', 'N/A')} - 复杂度: {item.get('complexity', 'N/A')}")

        # 3. 检查状态
        print(f"\n3. 状态持久化")
        print(f"  状态文件: {analyzer.state_file}")
        print(f"  上次分析时间: {analyzer.state['last_analysis_time']}")
        print(f"  已分析文件: {len(analyzer.state['analyzed_files'])} 个")
        # 4. 清除状态
        print("\n4. 清除状态...")
        analyzer.clear_state()
        print("状态已清除")

    except Exception as e:
        print(f"\n错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()