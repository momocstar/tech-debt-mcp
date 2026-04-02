# tools/complexity.py
import os
from utils import detect_language
from analyzers.java_ckjm import analyze_java_ckjm
from analyzers.python_radon import analyze_python_radon
from analyzers.generic_lizard import analyze_complexity_with_lizard
from analyzers.git_analyzer import get_changed_files
from config import get_config, get_complexity_threshold, get_max_items

def compute_complexity(project_path: str, max_items: int = None, since_commit: str = None,
                       progress_callback=None) -> dict:
    """
    计算代码复杂度

    Args:
        project_path: 项目根目录路径
        max_items: 最大返回项数（None 则使用配置值）
        since_commit: 可选，只分析自该 commit 以来的变更文件
        progress_callback: 进度回调函数 callback(current, total, message)

    Returns:
        包含复杂度分析结果的字典
    """
    # 使用配置值
    if max_items is None:
        max_items = get_max_items()

    config = get_config()

    # 验证项目路径
    if not project_path or not os.path.exists(project_path):
        return {
            "error": "项目路径不存在",
            "suggestion": f"请检查路径是否正确: {project_path}",
            "items": []
        }

    if progress_callback:
        progress_callback(0, 100, "检测项目语言...")

    lang = detect_language(project_path)

    # 获取变更文件列表（如果指定了 since_commit）
    changed_files = None
    if since_commit:
        if progress_callback:
            progress_callback(10, 100, f"获取 {since_commit} 以来的变更文件...")
        changed_files = get_changed_files(project_path, since_commit)

    if progress_callback:
        progress_callback(20, 100, f"开始分析 {lang} 代码复杂度...")

    # 根据语言选择分析器
    try:
        if lang in ['java', 'python', 'javascript', 'typescript', 'go']:
            items = analyze_complexity_with_lizard(
                project_path, since_commit, changed_files,
                progress_callback=lambda cur, tot, msg: progress_callback(20 + cur * 0.7, 100, msg) if progress_callback else None
            )
        else:
            # 回退到原有分析器
            if lang == 'java':
                items = analyze_java_ckjm(project_path, changed_files)
            elif lang == 'python':
                items = analyze_python_radon(project_path, changed_files)
            else:
                return {
                    "error": f"不支持的语言: {lang}",
                    "suggestion": "支持的语言: Java, Python, JavaScript, TypeScript, Go, C/C++",
                    "items": []
                }
    except Exception as e:
        return {
            "error": f"分析失败: {str(e)}",
            "suggestion": "请检查项目结构或查看日志文件",
            "items": []
        }

    if progress_callback:
        progress_callback(90, 100, "排序和过滤结果...")

    # 排序并截取
    items.sort(key=lambda x: x.complexity or 0, reverse=True)
    truncated = len(items) > max_items
    if truncated:
        items = items[:max_items]

    if progress_callback:
        progress_callback(100, 100, "分析完成")

    return {
        "items": [item.__dict__ for item in items],
        "total_count": len(items) if not truncated else "more than " + str(max_items),
        "truncated": truncated,
        "message": f"返回前{max_items}个高复杂度项。",
        "changed_files_count": len(changed_files) if changed_files else None,
        "language": lang
    }