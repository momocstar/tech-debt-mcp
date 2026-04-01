import subprocess
import xml.etree.ElementTree as ET
import os
from models import DebtItem, DebtType

def analyze_java_ckjm(project_path: str) -> list:
    """调用 CKJM 命令行工具并解析 XML 输出"""
    # 假设 CKJM 已安装，生成 XML 报告
    ckjm_jar = "/path/to/ckjm.jar"  # 实际使用时从环境变量读取
    output_xml = "/tmp/ckjm_output.xml"
    cmd = f"java -jar {ckjm_jar} -o {output_xml} {project_path}"
    subprocess.run(cmd, shell=True, capture_output=True)

    items = []
    tree = ET.parse(output_xml)
    root = tree.getroot()
    for class_elem in root.findall('class'):
        name = class_elem.get('name')
        wmc = float(class_elem.get('wmc', 0))  # 圈复杂度总和
        # 可进一步拆解方法
        for method in class_elem.findall('method'):
            method_name = method.get('name')
            complexity = float(method.get('cc', 0))
            if complexity > 10:  # 阈值
                items.append(DebtItem(
                    id=f"{name}.{method_name}",
                    type=DebtType.COMPLEX_METHOD,
                    file_path=f"{name}.java",  # 简化，实际需记录路径
                    entity_name=f"{name}.{method_name}",
                    complexity=complexity
                ))
    return items