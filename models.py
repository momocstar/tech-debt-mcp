from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum

class DebtType(str, Enum):
    COMPLEX_METHOD = "complex_method"
    LONG_METHOD = "long_method"
    GOD_CLASS = "god_class"
    DUPLICATE_CODE = "duplicate_code"
    LOW_COVERAGE = "low_coverage"

@dataclass
class DebtItem:
    id: str
    type: DebtType
    file_path: str
    entity_name: str          # 类名或方法名
    start_line: int = 0
    end_line: int = 0
    complexity: Optional[float] = None
    coverage: Optional[float] = None
    modification_frequency: int = 0
    business_impact: float = 1.0
    custom_notes: str = ""

    def debt_index(self, weights: Dict[str, float]) -> float:
        # 归一化函数
        def norm(value, max_val, min_val=0):
            return (value - min_val) / (max_val - min_val) if max_val > min_val else 0

        comp_score = norm(self.complexity or 0, 20, 0)  # 假设20为极高复杂度
        cov_score = 1 - (self.coverage or 0)            # 覆盖率越低债务越高
        biz_score = norm(self.business_impact, 5, 1)
        freq_score = norm(self.modification_frequency, 30, 0)  # 假设30次/半年为最高

        return (weights.get('complexity', 0.4) * comp_score +
                weights.get('coverage', 0.3) * cov_score +
                weights.get('business', 0.2) * biz_score +
                weights.get('frequency', 0.1) * freq_score)

@dataclass
class ScanResult:
    project_path: str
    items: List[DebtItem]
    total_count: int
    truncated: bool = False
    message: str = ""