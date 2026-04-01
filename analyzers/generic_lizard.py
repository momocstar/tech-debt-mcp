# analyzers/generic_lizard.py
import os
import lizard
from models import DebtItem, DebtType

def analyze_complexity_with_lizard(project_path: str, since_commit: str = None, changed_files: list = None) -> list:
    """
    使用 lizard 分析项目复杂度。
    如果提供了 changed_files，则只分析这些文件；否则全量扫描。
    """
    items = []

    # 支持的文件扩展名
    supported_exts = ('.py', '.java', '.js', '.ts', '.go', '.c', '.cpp', '.h', '.cs', '.rb', '.php')

    if changed_files is not None:
        # 只分析变更文件
        files_to_scan = [f for f in changed_files if os.path.exists(f) and f.endswith(supported_exts)]
    else:
        files_to_scan = None

    if files_to_scan:
        # 分析指定的文件列表
        for file_path in files_to_scan:
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
    else:
        # 全量扫描目录
        for root, _, files in os.walk(project_path):
            for f in files:
                if f.endswith(supported_exts):
                    filepath = os.path.join(root, f)
                    try:
                        file_analysis = lizard.analyze_file(filepath)
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
    return items