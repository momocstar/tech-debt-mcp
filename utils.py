# utils.py (修改后)
import os
import json

def detect_language(project_path: str) -> str:
    """通过文件后缀猜测项目主要语言，返回语言标识"""
    ext_count = {}
    for root, _, files in os.walk(project_path):
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in ['.java', '.py', '.js', '.ts', '.go', '.c', '.cpp', '.h', '.cs', '.rb', '.php']:
                ext_count[ext] = ext_count.get(ext, 0) + 1
    if not ext_count:
        return "unknown"
    # 将后缀映射到语言名
    ext_to_lang = {
        '.java': 'java',
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.go': 'go',
        '.c': 'c',
        '.cpp': 'cpp',
        '.h': 'c/cpp',
        '.cs': 'csharp',
        '.rb': 'ruby',
        '.php': 'php'
    }
    top_ext = max(ext_count, key=ext_count.get)
    return ext_to_lang.get(top_ext, 'unknown')

def load_json_report(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)