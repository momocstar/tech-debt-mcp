import lizard
import os
from models import DebtItem, DebtType

def analyze_complexity(project_path: str, file_list: list = None) -> list:
    items = []
    if file_list is None:
        # 全量扫描
        for root, _, files in os.walk(project_path):
            for file in files:
                if file.endswith(('.java', '.py', '.js', '.ts', '.go', '.jsx', '.tsx')):
                    file_list.append(os.path.join(root, file))
    for filepath in file_list:
        try:
            analysis = lizard.analyze_file(filepath)
            for func in analysis.function_list:
                if func.cyclomatic_complexity > 10:
                    items.append(DebtItem(
                        id=f"{filepath}:{func.name}",
                        type=DebtType.COMPLEX_METHOD,
                        file_path=filepath,
                        entity_name=func.name,
                        complexity=func.cyclomatic_complexity,
                        start_line=func.start_line,
                        end_line=func.end_line
                    ))
        except Exception as e:
            print(f"Error analyzing {filepath}: {e}")
    return items