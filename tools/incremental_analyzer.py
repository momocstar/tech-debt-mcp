"""
增量分析优化
支持状态持久化，避免每次全量扫描
"""
import os
import json
from typing import Dict, Optional
from git import Repo
from pathlib import Path
from datetime import datetime


class IncrementalAnalyzer:
    """增量分析器，支持状态持久化"""

    def __init__(self, project_path: str):
        self.project_path = project_path
        self.state_file = os.path.join(project_path, '.tech-debt-state.json')
        self._load_state()

    def _load_state(self):
        """加载上次分析状态"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    self.state = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                self.state = {
                    'last_commit': None,
                    'last_analysis_time': None,
                    'analyzed_files': []
                }
        else:
            self.state = {
                'last_commit': None,
                'last_analysis_time': None,
                'analyzed_files': []
            }

    def save_state(self, commit_hash: str, analysis_time: str, analyzed_files: list):
        """保存分析状态"""
        self.state['last_commit'] = commit_hash
        self.state['last_analysis_time'] = analysis_time
        self.state['analyzed_files'] = analyzed_files

        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)

    def get_changed_files_since_last_analysis(self) -> Optional[list]:
        """获取自上次分析以来的变更文件"""
        if not self.state['last_commit']:
            return None

        try:
            repo = Repo(self.project_path)

            # 获取上次分析的 commit
            last_commit = self.state['last_commit']

            # 获取变更文件
            changed_files = []
            for item in repo.iter_commits(f'{last_commit}..HEAD'):
                if item.a_path:
                    changed_files.append(item.a_path)

            return changed_files
        except Exception as e:
            print(f"获取变更文件失败: {e}")
            return None

    def analyze_incremental(self, since_commit: str = None,
                            progress_callback=None) -> Dict:
        """
        增量分析

        Args:
            since_commit: 起始 commit（如 'HEAD~5'）
            progress_callback: 进度回调函数

        Returns:
            增量分析结果
        """
        from tools.complexity import compute_complexity
        from tools.smells import detect_code_smells

        try:
            # 检查是否已分析过这些文件
            if self.state['last_commit']:
                changed_files = self.get_changed_files_since_last_analysis()

                if changed_files:
                    # 只分析变更的文件
                    if progress_callback:
                        progress_callback(0, len(changed_files), "获取变更文件列表...")

                    result = compute_complexity(
                        self.project_path,
                        max_items=100,
                        since_commit=None,
                        progress_callback=progress_callback
                    )

                    # 合并结果
                    all_items = result.get('items', [])
                    for file in changed_files:
                        file_result = detect_code_smells(
                            os.path.dirname(file),
                            max_items=5
                        )
                        if file_result.get('items'):
                            all_items.extend(file_result['items'])

                    if progress_callback:
                        progress_callback(50, 100, f"分析完成， 共检测到 {len(all_items)} 个债务项")

                    # 更新状态
                    self.save_state(
                        commit_hash='current',
                        analysis_time=str(datetime.now().isoformat()),
                        analyzed_files=changed_files
                    )

                    return {
                        "items": [item.__dict__ if hasattr(item, '__dict__') else item for item in all_items],
                        "total_count": len(all_items),
                        "incremental": True,
                        "changed_files": changed_files,
                        "message": f"增量分析完成， 共分析 {len(changed_files)} 个变更文件"
                    }
                else:
                    return {
                        "error": "未找到变更文件",
                        "suggestion": "使用 run_full_analysis() 进行全量分析"
                    }
            else:
                return {
                    "error": "未找到上次分析记录， 请先进行全量分析",
                    "suggestion": "使用 run_full_analysis() 进行全量分析"
                }
        except Exception as e:
            return {
                "error": f"增量分析失败: {str(e)}",
                "suggestion": "请检查 Git 仓库状态"
            }

    def clear_state(self):
        """清除状态文件"""
        if os.path.exists(self.state_file):
            os.remove(self.state_file)


def run_full_analysis(project_path: str, progress_callback=None) -> Dict:
    """全量分析"""
    from tools.complexity import compute_complexity
    from tools.smells import detect_code_smells

    if progress_callback:
        progress_callback(0, 100, "开始全量分析...")

    result = compute_complexity(
        project_path,
        max_items=100,
        progress_callback=progress_callback
    )

    smells_result = detect_code_smells(
        project_path,
        max_items=20
    )

    # 合并结果
    all_items = result.get('items', []) + smells_result.get('items', [])

    if progress_callback:
        progress_callback(90, 100, f"分析完成, 共检测到 {len(all_items)} 个债务项")

    # 保存状态
    analyzer = IncrementalAnalyzer(project_path)
    analyzer.save_state(
        commit_hash='full',
        analysis_time=str(datetime.now().isoformat()),
        analyzed_files=[]
    )

    return {
        "items": [item.__dict__ if hasattr(item, '__dict__') else item for item in all_items],
        "total_count": len(all_items),
        "incremental": False,
        "message": "全量分析完成"
    }


def run_incremental_analysis_demo():
    """运行增量分析示例"""

    print("\n" + "=" * 80)
    print("增量分析示例")
    print("=" * 80)

    analyzer = IncrementalAnalyzer('/Users/momoc/Desktop/xs/Intelligent-health-service')

    # 运行增量分析（自上次分析以来的变更)
    result = analyzer.analyze_incremental(progress_callback=lambda cur, tot, msg: print(f"[{cur}/{tot}] {msg}"))

    if result:
        print(f"\n分析完成: 共检测到 {len(result['items'])} 个债务项")
        print(f"增量模式: {result['incremental']}")
        print(f"变更文件: {len(result.get('changed_files', []))} 个")

        # 显示前 5 个债务项
        for i, item in enumerate(result['items'][:5], 1):
            print(f"{i}. {item['entity_name']} - 债务指数: {item.get('debt_score', 'N/A')}")

    analyzer.clear_state()


if __name__ == "__main__":
    run_incremental_analysis_demo()