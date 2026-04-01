"""
Tech-Debt-MCP 错误处理
提供统一的错误处理和友好的错误提示
"""


class TechDebtError(Exception):
    """技术债务分析基础异常"""

    def __init__(self, message: str, suggestion: str = None):
        self.message = message
        self.suggestion = suggestion
        super().__init__(self.message)

    def to_dict(self) -> dict:
        """转换为字典格式"""
        result = {"error": self.message}
        if self.suggestion:
            result["suggestion"] = self.suggestion
        return result


class ProjectNotFoundError(TechDebtError):
    """项目路径不存在"""

    def __init__(self, project_path: str):
        super().__init__(
            message=f"项目路径不存在: {project_path}",
            suggestion="请检查路径是否正确，确保项目目录存在"
        )


class InvalidProjectError(TechDebtError):
    """无效的项目"""

    def __init__(self, project_path: str, reason: str = None):
        message = f"无效的项目: {project_path}"
        if reason:
            message += f" ({reason})"
        super().__init__(
            message=message,
            suggestion="请确保项目目录包含源代码文件（Java, Python, JavaScript 等）"
        )


class UnsupportedLanguageError(TechDebtError):
    """不支持的语言"""

    def __init__(self, language: str):
        super().__init__(
            message=f"不支持的语言: {language}",
            suggestion="支持的语言: Java, Python, JavaScript, TypeScript, Go, C/C++"
        )


class AnalysisTimeoutError(TechDebtError):
    """分析超时"""

    def __init__(self, timeout: int):
        super().__init__(
            message=f"分析超时（{timeout}秒）",
            suggestion="项目过大，建议使用增量分析或增加超时时间（ANALYSIS_TIMEOUT 环境变量）"
        )


class DependencyError(TechDebtError):
    """依赖缺失错误"""

    def __init__(self, dependency: str, install_command: str):
        super().__init__(
            message=f"缺少依赖: {dependency}",
            suggestion=f"请运行: {install_command}"
        )


class ConfigurationError(TechDebtError):
    """配置错误"""

    def __init__(self, config_key: str, reason: str = None):
        message = f"配置错误: {config_key}"
        if reason:
            message += f" ({reason})"
        super().__init__(
            message=message,
            suggestion="请检查配置文件或环境变量设置"
        )


def handle_exception(e: Exception, context: str = None) -> dict:
    """
    统一处理异常

    Args:
        e: 异常对象
        context: 上下文信息

    Returns:
        包含错误信息的字典
    """
    if isinstance(e, TechDebtError):
        result = e.to_dict()
    else:
        result = {
            "error": str(e),
            "type": type(e).__name__
        }

    if context:
        result["context"] = context

    # 添加通用建议
    if "suggestion" not in result:
        result["suggestion"] = "请查看日志文件或联系支持"

    return result


def validate_project_path(project_path: str) -> None:
    """
    验证项目路径

    Raises:
        ProjectNotFoundError: 项目不存在
        InvalidProjectError: 无效的项目
    """
    import os

    if not project_path:
        raise ProjectNotFoundError("项目路径为空")

    if not os.path.exists(project_path):
        raise ProjectNotFoundError(project_path)

    if not os.path.isdir(project_path):
        raise InvalidProjectError(project_path, "路径不是目录")


def validate_source_files(project_path: str) -> None:
    """
    验证项目是否包含源代码文件

    Raises:
        InvalidProjectError: 项目不包含源代码
    """
    import os

    source_extensions = {'.java', '.py', '.js', '.ts', '.go', '.c', '.cpp', '.h'}
    found = False

    for root, _, files in os.walk(project_path):
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in source_extensions:
                found = True
                break
        if found:
            break

    if not found:
        raise InvalidProjectError(
            project_path,
            "未找到源代码文件"
        )