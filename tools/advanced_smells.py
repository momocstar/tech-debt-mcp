"""
高级代码坏味检测
检测更多类型的代码坏味
"""
import os
import re
from typing import List, Dict
from models import DebtItem, DebtType
from config import get_config


def detect_advanced_smells(project_path: str, max_items: int = 20) -> Dict:
    """
    检测高级代码坏味

    包括：
    - 深层嵌套
    - 魔法数字
    - 过长参数列表
    - 数据类
    - 过度注释
    """
    items = []

    # 深层嵌套检测
    items.extend(_detect_deep_nesting(project_path))

    # 魔法数字检测
    items.extend(_detect_magic_numbers(project_path))

    # 过长参数列表检测
    items.extend(_detect_long_parameter_list(project_path))

    # 数据类检测
    items.extend(_detect_data_classes(project_path))

    # 过度注释检测
    items.extend(_detect_excessive_comments(project_path))

    # 排序并返回
    items.sort(key=lambda x: x.complexity or 0, reverse=True)
    truncated = len(items) > max_items
    if truncated:
        items = items[:max_items]

    return {
        "items": [item.__dict__ for item in items],
        "total_count": len(items) if not truncated else f"more than {max_items}",
        "truncated": truncated,
        "message": f"检测到 {len(items)} 个高级代码坏味问题"
    }


def _detect_deep_nesting(project_path: str) -> List[DebtItem]:
    """检测深层嵌套（嵌套深度 > 4)"""
    items = []
    config = get_config()
    max_depth = config.get('MAX_NESTING_DEPTH', 4)

    # 支持的语言
    supported_extensions = {
        'java': '.java',
        'python': '.py',
        'javascript': '.js',
        'typescript': '.ts'
    }

    for root, _, files in os.walk(project_path):
        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            if ext not in supported_extensions:
                continue

            filepath = os.path.join(root, filename)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # 计算嵌套深度
                depth = _calculate_nesting_depth(content)
                if depth > max_depth:
                    items.append(DebtItem(
                        id=f"{filepath}:deep_nesting",
                        type=DebtType.DEEP_NESTING,
                        file_path=filepath,
                        entity_name=os.path.basename(filepath),
                        complexity=depth,
                        custom_notes=f"嵌套深度: {depth}，建议重构"
                    ))
            except Exception:
                continue

    return items


def _calculate_nesting_depth(code: str) -> int:
    """计算代码的最大嵌套深度"""
    max_depth = 0
    current_depth = 0

    for line in code.split('\n'):
        stripped = line.strip()

        if not stripped:
            continue

        # 计算缩进
        indent = len(line) - len(line.lstrip())
        depth = indent // 4

        if depth > current_depth:
            current_depth = depth

        if '{' in line:
            current_depth += 1
        if '}' in line:
            current_depth -= 1

        max_depth = max(max_depth, current_depth)

    return max_depth


def _detect_magic_numbers(project_path: str) -> List[DebtItem]:
    """检测魔法数字（硬编码的数字常量)"""
    items = []

    # 数字正则表达式
    number_pattern = r'\b\d+\b|\b\d+\.\d+\b|\b0[xX][0-9aA-Fa-f]+'

    for root, _, files in os.walk(project_path):
        for filename in files:
            if not filename.endswith(('.java', '.py', '.js', '.ts')):
                continue

            filepath = os.path.join(root, filename)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # 查找魔法数字
                matches = re.finditer(number_pattern, content)
                for match in matches:
                    number = match.group()
                    # 检查是否是常量定义
                    if not _is_constant_definition(content, match.start()):
                        items.append(DebtItem(
                            id=f"{filepath}:magic_number_{number}",
                            type=DebtType.MAGIC_NUMBER,
                            file_path=filepath,
                            entity_name=f"魔法数字: {number}",
                            complexity=5,
                            start_line=content[:match.start()].count('\n') + 1,
                            custom_notes=f"硬编码数字， {number}，建议使用常量"
                        ))
            except Exception:
                continue

    return items


def _is_constant_definition(content: str, position: int) -> bool:
    """检查是否是常量定义"""
    # 检查前后文
    before = content[:position-50:position]
    after_start = position + 10

    after = content[position + 10:position + 50]

    # 检查是否在常量声明附近
    patterns = [
        r'const\s+\w+\s*=',
        r'private\s+\w+\s+\s*=',
        r'public\s+\w+\s+\s*=',
        r'static\s+\w+\s+\s*=',
        r'final\s+\w+\s+=',
    ]

    before_text = before[after_start:after].lower()
    for pattern in patterns:
        if pattern in before_text:
            return True

    return False


def _detect_long_parameter_list(project_path: str) -> List[DebtItem]:
    """检测过长参数列表（参数数量 > 5)"""
    items = []

    try:
        import javalang
        use_ast = True
    except ImportError:
        # 后备方案：简单文本匹配
        return _detect_long_parameter_list_fallback(project_path)

    for root, _, files in os.walk(project_path):
        for filename in files:
            if not filename.endswith('.java'):
                continue

            filepath = os.path.join(root, filename)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                try:
                    tree = javalang.parse.parse(content)

                    for path, node in tree.filter(javalang.tree.MethodDeclaration):
                        if node.parameters:
                            param_count = len(node.parameters)
                            if param_count > 5:
                                items.append(DebtItem(
                                    id=f"{filepath}:{node.name}",
                                    type=DebtType.LONG_PARAMETER_LIST,
                                    file_path=filepath,
                                    entity_name=node.name,
                                    complexity=param_count,
                                    start_line=node.position.line if node.position else 0,
                                    end_line=0,
                                    custom_notes=f"参数数量: {param_count}，建议减少参数"
                                ))
                except Exception:
                    continue
            except Exception:
                continue

    return items


def _detect_long_parameter_list_fallback(project_path: str) -> List[DebtItem]:
    """后备方案检测过长参数列表"""
    items = []

    for root, _, files in os.walk(project_path):
        for filename in files:
            if not filename.endswith(('.java', '.py')):
                continue

            filepath = os.path.join(root, filename)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # 简单的方法参数匹配
                method_pattern = r'(public|private|protected)\s+\w+\s+\s+\w+\s*\([^)]*\)'
                matches = re.finditer(method_pattern, content)

                for match in matches:
                    param_list_str = match.group(1)
                    # 计算参数数量
                    param_count = param_list_str.count(',')
                    if param_count > 5:
                        items.append(DebtItem(
                            id=f"{filepath}:{_extract_method_name(match)}",
                            type=DebtType.LONG_PARAMETER_LIST,
                            file_path=filepath,
                            entity_name=_extract_method_name(match),
                            complexity=param_count,
                            custom_notes=f"参数数量: {param_count}，建议减少"
                        ))
            except Exception:
                continue

    return items


def _extract_method_name(match) -> str:
    """从匹配中提取方法名"""
    text = match.group(0)
    # 查找方法名（第一个单词）
    parts = text.split()
    if len(parts) >= 2:
        return parts[1].split('(')[0]
    return "unknown"


def _detect_data_classes(project_path: str) -> List[DebtItem]:
    """检测数据类（只有 getter/setter）"""
    items = []

    for root, _, files in os.walk(project_path):
        for filename in files:
            if not filename.endswith(('.java', '.py')):
                continue

            filepath = os.path.join(root, filename)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # 统计 getter/setter 数量
                getter_count = content.count('get ')
                setter_count = content.count('set ')

                # 如果 getter/setter 数量过多
                if getter_count + setter_count > 10:
                    class_name = os.path.splitext(filename)[0]
                    items.append(DebtItem(
                        id=f"{filepath}:{class_name}",
                        type=DebtType.DATA_CLASS,
                        file_path=filepath,
                        entity_name=class_name,
                        complexity=getter_count + setter_count,
                        custom_notes=f"包含 {getter_count} 个 getter 和 {setter_count} 个 setter，建议封装数据"
                    ))
            except Exception:
                continue
    return items


def _detect_excessive_comments(project_path: str) -> List[DebtItem]:
    """检测过度注释（注释占比 > 30%)"""
    items = []

    for root, _, files in os.walk(project_path):
        for filename in files:
            if not filename.endswith(('.java', '.py', '.js', '.ts')):
                continue

            filepath = os.path.join(root, filename)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # 计算注释行数
                total_lines = len(content.split('\n'))
                comment_lines = 0

                for line in content.split('\n'):
                    stripped = line.strip()
                    if stripped.startswith('//') or stripped.startswith('#') or stripped.startswith('/*'):
                        comment_lines += 1

                # 计算注释占比
                if total_lines > 0:
                    comment_ratio = comment_lines / total_lines
                    if comment_ratio > 0.3:
                        items.append(DebtItem(
                            id=f"{filepath}:excessive_comments",
                            type=DebtType.EXCESSIVE_COMMENTS,
                            file_path=filepath,
                            entity_name=os.path.basename(filepath),
                            complexity=comment_ratio,
                            custom_notes=f"注释占比 {comment_ratio:.1%}，建议精简注释"
                        ))
            except Exception:
                continue

    return items