"""
Tech-Debt-MCP 错误处理和验证模块
提供友好的错误提示和配置验证
"""
import os
import sys
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]


class ErrorHandler:
    """统一错误处理"""

    @staticmethod
    def format_error(error_type: str, message: str, suggestion: str = None) -> Dict:
        """
        格式化错误信息

        Args:
            error_type: 错误类型
            message: 错误消息
            suggestion: 解决建议

        Returns:
            格式化的错误字典
        """
        result = {
            "error": error_type,
            "message": message,
        }

        if suggestion:
            result["suggestion"] = suggestion

        return result

    @staticmethod
    def project_not_found(project_path: str) -> Dict:
        """项目路径不存在错误"""
        return ErrorHandler.format_error(
            "ProjectNotFoundError",
            f"项目路径不存在: {project_path}",
            f"请检查路径是否正确，确保目录存在: {project_path}"
        )

    @staticmethod
    def invalid_project_structure(project_path: str) -> Dict:
        """项目结构无效错误"""
        return ErrorHandler.format_error(
            "InvalidProjectStructureError",
            f"项目结构无效，未找到源代码: {project_path}",
            "确保项目包含源代码文件（Java: .java, Python: .py, JavaScript: .js 等）"
        )

    @staticmethod
    def analysis_timeout(timeout: int) -> Dict:
        """分析超时错误"""
        return ErrorHandler.format_error(
            "AnalysisTimeoutError",
            f"分析超时，超过 {timeout} 秒",
            f"可以增加超时时间: export ANALYSIS_TIMEOUT={timeout * 2}"
        )

    @staticmethod
    def dependency_missing(dependency: str, install_cmd: str) -> Dict:
        """依赖缺失错误"""
        return ErrorHandler.format_error(
            "DependencyMissingError",
            f"缺少依赖: {dependency}",
            f"运行以下命令安装: {install_cmd}"
        )

    @staticmethod
    def unsupported_language(language: str) -> Dict:
        """不支持的语言错误"""
        return ErrorHandler.format_error(
            "UnsupportedLanguageError",
            f"不支持的语言: {language}",
            "支持的语言: Java, Python, JavaScript, TypeScript, Go, C/C++"
        )

    @staticmethod
    def git_repository_required(project_path: str) -> Dict:
        """需要 Git 仓库错误"""
        return ErrorHandler.format_error(
            "GitRepositoryRequiredError",
            "增量分析需要 Git 仓库",
            f"请先初始化 Git 仓库: cd {project_path} && git init"
        )


class ConfigValidator:
    """配置验证器"""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.suggestions = []

    def validate_all(self) -> ValidationResult:
        """运行所有验证"""
        self.errors = []
        self.warnings = []
        self.suggestions = []

        # 验证 Python 版本
        self._validate_python_version()

        # 验证依赖库
        self._validate_dependencies()

        # 验证环境变量
        self._validate_environment_variables()

        # 验证文件权限
        self._validate_file_permissions()

        # 验证配置参数
        self._validate_config_parameters()

        return ValidationResult(
            is_valid=len(self.errors) == 0,
            errors=self.errors,
            warnings=self.warnings,
            suggestions=self.suggestions
        )

    def _validate_python_version(self):
        """验证 Python 版本"""
        required_version = (3, 8)
        current_version = sys.version_info[:2]

        if current_version < required_version:
            self.errors.append(
                f"Python 版本过低: {'.'.join(map(str, current_version))}, "
                f"需要 {'.'.join(map(str, required_version))} 或更高版本"
            )
            self.suggestions.append(
                "请升级 Python: brew install python@3.12 (macOS) 或访问 python.org"
            )

    def _validate_dependencies(self):
        """验证依赖库"""
        dependencies = {
            'lizard': 'lizard>=1.17.10',
            'radon': 'radon>=6.0.1',
            'git': 'gitpython>=3.1.41',
            'requests': 'requests>=2.31.0',
        }

        missing = []
        for module, package in dependencies.items():
            try:
                __import__(module)
            except ImportError:
                missing.append(package)

        if missing:
            self.errors.append(f"缺少依赖库: {', '.join(missing)}")
            self.suggestions.append(
                f"运行: pip install {' '.join(missing)}"
            )

        # 检查可选依赖
        try:
            import javalang
        except ImportError:
            self.warnings.append(
                "javalang 未安装，代码坏味检测将使用后备方案（准确度较低）"
            )
            self.suggestions.append(
                "建议安装: pip install javalang>=0.13.0"
            )

    def _validate_environment_variables(self):
        """验证环境变量"""
        # 检查 CKJM_JAR
        ckjm_jar = os.getenv('CKJM_JAR')
        if ckjm_jar:
            if not os.path.exists(ckjm_jar):
                self.warnings.append(
                    f"CKJM_JAR 文件不存在: {ckjm_jar}"
                )
                self.suggestions.append(
                    "Java 复杂度分析将使用 lizard 作为后备"
                )
        else:
            self.warnings.append(
                "未设置 CKJM_JAR 环境变量"
            )

        # 检查 SonarQube 配置
        sonar_url = os.getenv('SONARQUBE_URL')
        sonar_token = os.getenv('SONARQUBE_TOKEN')
        if sonar_url and not sonar_token:
            self.warnings.append(
                "已设置 SONARQUBE_URL 但缺少 SONARQUBE_TOKEN"
            )

        # 检查 AI 建议配置
        enable_ai = os.getenv('ENABLE_AI_SUGGESTIONS', 'false').lower() == 'true'
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if enable_ai and not api_key:
            self.warnings.append(
                "已启用 AI 建议但缺少 ANTHROPIC_API_KEY"
            )

    def _validate_file_permissions(self):
        """验证文件权限"""
        # 检查当前目录写权限
        current_dir = os.getcwd()
        if not os.access(current_dir, os.W_OK):
            self.errors.append(
                f"当前目录无写权限: {current_dir}"
            )

    def _validate_config_parameters(self):
        """验证配置参数"""
        from config import get_config

        config = get_config()

        # 验证权重总和
        weights = config.get_weights()
        weight_sum = sum(weights.values())

        if abs(weight_sum - 1.0) > 0.01:
            self.errors.append(
                f"债务指数权重总和不为 1.0: {weight_sum:.2f}"
            )
            self.suggestions.append(
                "调整权重配置，确保总和为 1.0"
            )

        # 验证阈值合理性
        complexity_threshold = config.get('COMPLEXITY_THRESHOLD')
        if complexity_threshold < 5 or complexity_threshold > 50:
            self.warnings.append(
                f"复杂度阈值异常: {complexity_threshold}（推荐: 10-20）"
            )

        max_items = config.get('MAX_ITEMS')
        if max_items > 100:
            self.warnings.append(
                f"最大返回项数过大: {max_items}，可能影响性能"
            )


def validate_setup() -> ValidationResult:
    """验证环境设置"""
    validator = ConfigValidator()
    return validator.validate_all()


def print_validation_result(result: ValidationResult):
    """打印验证结果"""
    print("\n" + "=" * 80)
    print("Tech-Debt-MCP 环境验证")
    print("=" * 80)

    if result.is_valid:
        print("\n✅ 环境验证通过")
    else:
        print("\n❌ 环境验证失败")

    if result.errors:
        print("\n🔴 错误:")
        for error in result.errors:
            print(f"  - {error}")

    if result.warnings:
        print("\n🟡 警告:")
        for warning in result.warnings:
            print(f"  - {warning}")

    if result.suggestions:
        print("\n💡 建议:")
        for suggestion in result.suggestions:
            print(f"  - {suggestion}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    result = validate_setup()
    print_validation_result(result)

    sys.exit(0 if result.is_valid else 1)