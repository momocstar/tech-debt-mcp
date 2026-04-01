import os
import hashlib
from collections import defaultdict
from models import DebtItem, DebtType
from config import get_long_method_lines, get_god_class_methods, get_god_class_lines, get_duplicate_block_size

def detect_code_smells(project_path: str, max_items: int = 20) -> dict:
    """
    检测代码坏味：长方法、上帝类、重复代码
    使用 AST 解析提高准确性
    """
    items = []

    # 1. 长方法检测
    long_methods = _detect_long_methods_ast(project_path)
    items.extend(long_methods)

    # 2. 上帝类检测
    god_classes = _detect_god_classes_ast(project_path)
    items.extend(god_classes)

    # 3. 重复代码检测
    duplicates = _detect_duplicates(project_path)
    items.extend(duplicates)

    # 按严重程度排序
    items.sort(key=lambda x: x.complexity or 0, reverse=True)
    truncated = len(items) > max_items
    if truncated:
        items = items[:max_items]

    return {
        "items": [item.__dict__ for item in items],
        "total_count": len(items) if not truncated else "more than " + str(max_items),
        "truncated": truncated,
        "message": f"检测到 {len(items)} 个代码坏味问题"
    }


def _detect_long_methods_ast(project_path: str) -> list:
    """
    使用 AST 解析检测长方法（方法行数 > 50）
    """
    items = []

    # 尝试导入 javalang
    try:
        import javalang
    except ImportError:
        # 如果没有 javalang，回退到改进的文本解析
        return _detect_long_methods_fallback(project_path)

    for root, _, files in os.walk(project_path):
        for filename in files:
            if not filename.endswith('.java'):
                continue

            filepath = os.path.join(root, filename)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # 解析 Java AST
                tree = javalang.parse.parse(content)

                # 遍历所有方法声明
                for path, node in tree.filter(javalang.tree.MethodDeclaration):
                    if node.position:
                        start_line = node.position.line
                        end_line = _find_method_end(content, start_line)
                        length = end_line - start_line + 1

                        if length > get_long_method_lines():  # 长方法阈值（可配置）
                            items.append(DebtItem(
                                id=f"{filepath}:{node.name}",
                                type=DebtType.LONG_METHOD,
                                file_path=filepath,
                                entity_name=node.name,
                                complexity=length,
                                start_line=start_line,
                                end_line=end_line,
                                custom_notes=f"方法长度 {length} 行，建议拆分"
                            ))

            except Exception as e:
                # 跳过无法解析的文件
                continue

    return items


def _detect_long_methods_fallback(project_path: str) -> list:
    """
    改进的文本解析方法（作为后备方案）
    """
    items = []

    for root, _, files in os.walk(project_path):
        for filename in files:
            if not filename.endswith('.java'):
                continue

            filepath = os.path.join(root, filename)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()

                # 改进的方法检测逻辑
                brace_count = 0
                in_method = False
                method_start = 0
                method_name = ""

                for i, line in enumerate(lines, 1):
                    stripped = line.strip()

                    # 检测方法开始（更准确的模式）
                    if not in_method:
                        # 匹配方法签名: public/private/protected 返回类型 方法名(
                        if _is_method_signature(stripped):
                            in_method = True
                            method_start = i
                            method_name = _extract_method_name(stripped)
                            brace_count = stripped.count('{') - stripped.count('}')
                    else:
                        # 在方法内部，计算大括号
                        brace_count += stripped.count('{') - stripped.count('}')

                        # 方法结束
                        if brace_count == 0 and '{' in line:
                            length = i - method_start + 1
                            if length > get_long_method_lines():  # 长方法阈值（可配置）
                                items.append(DebtItem(
                                    id=f"{filepath}:{method_name}",
                                    type=DebtType.LONG_METHOD,
                                    file_path=filepath,
                                    entity_name=method_name,
                                    complexity=length,
                                    start_line=method_start,
                                    end_line=i,
                                    custom_notes=f"方法长度 {length} 行"
                                ))
                            in_method = False

            except Exception:
                continue

    return items


def _is_method_signature(line: str) -> bool:
    """判断是否是方法签名"""
    # 排除类声明、接口声明等
    if any(keyword in line for keyword in ['class ', 'interface ', 'enum ', '@interface']):
        return False

    # 必须包含 ( 和可能是方法
    if '(' not in line:
        return False

    # 排除注解
    if line.startswith('@'):
        return False

    # 检查是否有方法修饰符或返回类型
    method_indicators = ['public ', 'private ', 'protected ', 'static ', 'final ',
                        'void ', 'int ', 'String ', 'boolean ', 'long ', 'double ',
                        'List<', 'Map<', 'Set<', 'Optional<']

    return any(indicator in line for indicator in method_indicators)


def _extract_method_name(line: str) -> str:
    """从方法签名中提取方法名"""
    try:
        # 找到方法名（在 ( 之前的最后一个单词）
        parts = line.split('(')[0].strip().split()
        if parts:
            return parts[-1].replace('{', '').strip()
    except:
        pass
    return "unknown"


def _find_method_end(content: str, start_line: int) -> int:
    """找到方法的结束行"""
    lines = content.split('\n')
    if start_line > len(lines):
        return start_line

    brace_count = 0
    found_opening = False

    for i in range(start_line - 1, len(lines)):
        line = lines[i]
        brace_count += line.count('{') - line.count('}')

        if '{' in line and not found_opening:
            found_opening = True

        if found_opening and brace_count == 0:
            return i + 1  # 行号从1开始

    return len(lines)


def _detect_god_classes_ast(project_path: str) -> list:
    """
    检测上帝类（方法数 > 20 或 行数 > 500）
    """
    items = []

    try:
        import javalang
    except ImportError:
        return _detect_god_classes_fallback(project_path)

    for root, _, files in os.walk(project_path):
        for filename in files:
            if not filename.endswith('.java'):
                continue

            filepath = os.path.join(root, filename)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                tree = javalang.parse.parse(content)

                # 统计方法数
                method_count = 0
                for path, node in tree.filter(javalang.tree.MethodDeclaration):
                    method_count += 1

                # 统计行数
                line_count = len(content.split('\n'))

                # 判断是否为上帝类
                if method_count > get_god_class_methods() or line_count > get_god_class_lines():
                    class_name = filename.replace('.java', '')

                    # 获取类声明的位置
                    start_line = 1
                    for path, node in tree.filter(javalang.tree.ClassDeclaration):
                        if node.position:
                            start_line = node.position.line
                        break

                    items.append(DebtItem(
                        id=f"{filepath}:{class_name}",
                        type=DebtType.GOD_CLASS,
                        file_path=filepath,
                        entity_name=class_name,
                        complexity=max(method_count, line_count // 25),
                        start_line=start_line,
                        end_line=line_count,
                        custom_notes=f"方法数: {method_count}, 行数: {line_count}"
                    ))

            except Exception:
                continue

    return items


def _detect_god_classes_fallback(project_path: str) -> list:
    """改进的上帝类检测后备方案"""
    items = []

    for root, _, files in os.walk(project_path):
        for filename in files:
            if not filename.endswith('.java'):
                continue

            filepath = os.path.join(root, filename)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # 统计方法数（改进的正则）
                import re
                # 匹配方法声明
                method_pattern = r'(public|private|protected|static|final)\s+[\w<>[\],\s]+\s+\w+\s*\([^)]*\)\s*(?:throws\s+[\w,\s]+)?\s*\{'
                method_count = len(re.findall(method_pattern, content))

                # 统计行数
                line_count = len(content.split('\n'))

                if method_count > get_god_class_methods() or line_count > get_god_class_lines():
                    class_name = filename.replace('.java', '')
                    items.append(DebtItem(
                        id=f"{filepath}:{class_name}",
                        type=DebtType.GOD_CLASS,
                        file_path=filepath,
                        entity_name=class_name,
                        complexity=max(method_count, line_count // 25),
                        custom_notes=f"方法数: {method_count}, 行数: {line_count}"
                    ))

            except Exception:
                continue

    return items


def _detect_duplicates(project_path: str) -> list:
    """
    检测重复代码块（连续10行代码重复出现）
    """
    blocks = defaultdict(list)

    for root, _, files in os.walk(project_path):
        for filename in files:
            if not filename.endswith(('.java', '.py')):
                continue

            filepath = os.path.join(root, filename)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # 按行分割，去除空白和注释
                lines = []
                for line in content.split('\n'):
                    stripped = line.strip()
                    # 跳过空行、单行注释、import 语句
                    if (stripped and
                        not stripped.startswith('//') and
                        not stripped.startswith('#') and
                        not stripped.startswith('import ') and
                        not stripped.startswith('package ')):
                        lines.append(stripped)

                # 检测重复代码块
                block_size = get_duplicate_block_size()
                for i in range(len(lines) - block_size):
                    block = '\n'.join(lines[i:i+block_size])
                    # 标准化：去除多余空格
                    block = ' '.join(block.split())
                    block_hash = hashlib.md5(block.encode()).hexdigest()
                    blocks[block_hash].append((filepath, i+1))

            except Exception:
                continue

    items = []
    seen_blocks = set()

    for block_hash, locations in blocks.items():
        if len(locations) >= 2:
            filepath, line = locations[0]

            # 避免重复报告同一个代码块
            if filepath not in seen_blocks:
                items.append(DebtItem(
                    id=f"{filepath}:dup_{block_hash[:8]}",
                    type=DebtType.DUPLICATE_CODE,
                    file_path=filepath,
                    entity_name=f"重复代码块 (出现 {len(locations)} 次)",
                    complexity=len(locations),
                    start_line=line,
                    end_line=line + block_size,
                    custom_notes=f"在 {len(locations)} 个位置重复出现"
                ))
                seen_blocks.add(filepath)

    return items