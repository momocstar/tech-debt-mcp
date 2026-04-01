"""
Tech-Debt-MCP 配置管理
支持通过环境变量自定义检测参数
"""
import os
from typing import Dict, Any


class Config:
    """配置管理类"""

    # 默认配置值
    DEFAULTS = {
        # 复杂度分析参数
        'COMPLEXITY_THRESHOLD': 10,  # 圈复杂度阈值
        'MAX_ITEMS': 20,  # 最大返回项数

        # 代码坏味检测参数
        'LONG_METHOD_LINES': 50,  # 长方法行数阈值
        'GOD_CLASS_METHODS': 20,  # 上帝类方法数阈值
        'GOD_CLASS_LINES': 500,  # 上帝类行数阈值
        'DUPLICATE_BLOCK_SIZE': 10,  # 重复代码块大小

        # 债务指数权重
        'WEIGHT_COMPLEXITY': 0.4,  # 复杂度权重
        'WEIGHT_COVERAGE': 0.3,  # 覆盖率权重
        'WEIGHT_BUSINESS': 0.2,  # 业务影响权重
        'WEIGHT_FREQUENCY': 0.1,  # 修改频率权重

        # 分析选项
        'EXCLUDE_PATTERNS': 'test*,tests*,*Test*,*test*',  # 排除的文件模式
        'ENABLE_AI_SUGGESTIONS': False,  # 是否启用 AI 建议

        # 性能参数
        'ANALYSIS_TIMEOUT': 300,  # 分析超时时间（秒）
        'MAX_FILE_SIZE': 1048576,  # 最大文件大小（1MB）
    }

    _instance = None
    _config = {}

    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """加载配置（从环境变量）"""
        for key, default_value in self.DEFAULTS.items():
            env_value = os.getenv(key)

            if env_value is not None:
                # 根据默认值类型进行转换
                if isinstance(default_value, bool):
                    self._config[key] = env_value.lower() in ('true', '1', 'yes')
                elif isinstance(default_value, int):
                    self._config[key] = int(env_value)
                elif isinstance(default_value, float):
                    self._config[key] = float(env_value)
                elif isinstance(default_value, str):
                    self._config[key] = env_value
                else:
                    self._config[key] = env_value
            else:
                self._config[key] = default_value

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self._config.get(key, default)

    def get_weights(self) -> Dict[str, float]:
        """获取债务指数权重配置"""
        return {
            'complexity': self.get('WEIGHT_COMPLEXITY'),
            'coverage': self.get('WEIGHT_COVERAGE'),
            'business': self.get('WEIGHT_BUSINESS'),
            'frequency': self.get('WEIGHT_FREQUENCY')
        }

    def get_exclude_patterns(self) -> list:
        """获取排除模式列表"""
        patterns = self.get('EXCLUDE_PATTERNS')
        return [p.strip() for p in patterns.split(',')]

    def update(self, key: str, value: Any):
        """更新配置值"""
        self._config[key] = value

    def reset(self):
        """重置为默认配置"""
        self._config = self.DEFAULTS.copy()

    def to_dict(self) -> Dict[str, Any]:
        """导出为字典"""
        return self._config.copy()

    def __repr__(self) -> str:
        """字符串表示"""
        return f"Config({self._config})"


# 全局配置实例
config = Config()


def get_config() -> Config:
    """获取配置实例"""
    return config


# 便捷函数
def get_complexity_threshold() -> int:
    """获取复杂度阈值"""
    return config.get('COMPLEXITY_THRESHOLD')


def get_max_items() -> int:
    """获取最大返回项数"""
    return config.get('MAX_ITEMS')


def get_long_method_lines() -> int:
    """获取长方法行数阈值"""
    return config.get('LONG_METHOD_LINES')


def get_god_class_methods() -> int:
    """获取上帝类方法数阈值"""
    return config.get('GOD_CLASS_METHODS')


def get_god_class_lines() -> int:
    """获取上帝类行数阈值"""
    return config.get('GOD_CLASS_LINES')


def get_duplicate_block_size() -> int:
    """获取重复代码块大小"""
    return config.get('DUPLICATE_BLOCK_SIZE')