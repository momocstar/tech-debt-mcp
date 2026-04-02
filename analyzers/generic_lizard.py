# analyzers/generic_lizard.py
import os
import lizard
from models import DebtItem, DebtType
from typing import Callable, List, Optional

def analyze_complexity_with_lizard(project_path: str, since_commit: str = None,
                                   changed_files: list = None,
                                   progress_callback: Optional[Callable[[int, int, str], None]] = None) -> List[DebtItem]:
    """
    使用 lizard 分析项目复杂度。
    如果提供了 changed_files，则只分析这些文件；否则全量扫描。

    Args:
        project_path: 项目根目录
        since_commit: 起始 commit（用于记录，实际过滤由 changed_files 控制）
        changed_files: 要分析的文件列表
        progress_callback: 进度回调函数 callback(current, total, message)
    """
    items = []

    # 支持的文件扩展名
    supported_exts = ('.py', '.java', '.js', '.ts', '.go', '.c', '.cpp', '.h', '.cs', '.rb', '.php')

    if changed_files is not None:
        # 只分析变更文件
        files_to_scan = [f for f in changed_files if os.path.exists(f) and f.endswith(supported_exts)]
    else:
        # 全量扫描：收集所有支持的文件
        files_to_scan = []
        for root, _, files in os.walk(project_path):
            for f in files:
                if f.endswith(supported_exts):
                    files_to_scan.append(os.path.join(root, f))

    total_files = len(files_to_scan)
    if progress_callback and total_files > 0:
        progress_callback(0, total_files, f"准备分析 {total_files} 个文件...")

    for idx, file_path in enumerate(files_to_scan):
        try:
            file_analysis = lizard.analyze_file(file_path)
            for func in file_analysis.function_list:
                if func.cyclomatic_complexity > 10:
                    items.append(DebtItem(
                        id=f"{func.filename}:{func.name}",
                        type=DebtType.COMPLEX_METHOD,
                        file_path=func.filename,
                        entity_name=func.name,
                        complexity=func.cyclomatic_complexity,
                        start_line=func.start_line,
                        end_line=func.end_line
                    ))
        except Exception:
            continue

        if progress_callback and idx % 10 == 0:
            progress_callback(idx + 1, total_files, f"已分析 {idx + 1}/{total_files} 个文件")

    if progress_callback:
        progress_callback(total_files, total_files, f"分析完成，发现 {len(items)} 个高复杂度方法")

    return items