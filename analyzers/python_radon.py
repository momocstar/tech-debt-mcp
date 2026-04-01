import radon.complexity as radon_cc
import os
from models import DebtItem, DebtType

def analyze_python_radon(project_path: str) -> list:
    items = []
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                try:
                    blocks = radon_cc.cc_visit(content)
                    for block in blocks:
                        if block.complexity > 10:
                            items.append(DebtItem(
                                id=f"{filepath}:{block.name}",
                                type=DebtType.COMPLEX_METHOD,
                                file_path=filepath,
                                entity_name=block.name,
                                complexity=block.complexity
                            ))
                except Exception as e:
                    print(f"Error analyzing {filepath}: {e}")
    return items