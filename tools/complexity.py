# tools/complexity.py
from utils import detect_language
from analyzers.java_ckjm import analyze_java_ckjm
from analyzers.python_radon import analyze_python_radon
from analyzers.generic_lizard import analyze_complexity_with_lizard
from analyzers.git_analyzer import get_changed_files
def compute_complexity(project_path: str, max_items: int = 20, since_commit: str = None) -> dict:
    """
    since_commit: 可选，只分析自该 commit 以来的变更文件。可以是 commit hash 或 'HEAD~5' 等。
    """
    lang = detect_language(project_path)

    # 获取变更文件列表（如果指定了 since_commit）
    changed_files = None
    if since_commit:
        changed_files = get_changed_files(project_path, since_commit)

    # 根据语言选择分析器，但 lizard 支持多语言，可优先使用
    if lang in ['java', 'python', 'javascript', 'typescript', 'go']:
        items = analyze_complexity_with_lizard(project_path, since_commit, changed_files)
    else:
        # 回退到原有分析器（但可能不支持所有语言）
        if lang == 'java':
            items = analyze_java_ckjm(project_path, changed_files)  # 需扩展 java_ckjm 支持过滤
        elif lang == 'python':
            items = analyze_python_radon(project_path, changed_files)
        else:
            return {"error": f"Unsupported language: {lang}", "items": []}

    # 排序并截取
    items.sort(key=lambda x: x.complexity or 0, reverse=True)
    truncated = len(items) > max_items
    if truncated:
        items = items[:max_items]

    return {
        "items": [item.__dict__ for item in items],
        "total_count": len(items) if not truncated else "more than " + str(max_items),
        "truncated": truncated,
        "message": f"返回前{max_items}个高复杂度项。",
        "changed_files_count": len(changed_files) if changed_files else None
    }