# Tech-Debt-MCP 配置说明

## 环境变量配置

Tech-Debt-MCP 支持通过环境变量自定义检测参数，所有参数都有合理的默认值。

### 配置方式

#### 方式 1: 系统环境变量

```bash
# 设置复杂度阈值
export COMPLEXITY_THRESHOLD=15

# 设置最大返回项数
export MAX_ITEMS=30

# 设置长方法行数阈值
export LONG_METHOD_LINES=60

# 设置债务指数权重
export WEIGHT_COMPLEXITY=0.5
export WEIGHT_COVERAGE=0.25
export WEIGHT_BUSINESS=0.15
export WEIGHT_FREQUENCY=0.1
```

#### 方式 2: .env 文件

在项目根目录创建 `.env` 文件：

```env
# 复杂度分析参数
COMPLEXITY_THRESHOLD=10
MAX_ITEMS=20

# 代码坏味检测参数
LONG_METHOD_LINES=50
GOD_CLASS_METHODS=20
GOD_CLASS_LINES=500
DUPLICATE_BLOCK_SIZE=10

# 债务指数权重
WEIGHT_COMPLEXITY=0.4
WEIGHT_COVERAGE=0.3
WEIGHT_BUSINESS=0.2
WEIGHT_FREQUENCY=0.1

# 性能参数
ANALYSIS_TIMEOUT=300
MAX_FILE_SIZE=1048576
```

#### 方式 3: MCP 配置文件

在 `.mcp.json` 中配置：

```json
{
  "mcpServers": {
    "tech-debt": {
      "command": "/path/to/tech-debt-mcp/dist/tech-debt-mcp",
      "env": {
        "COMPLEXITY_THRESHOLD": "15",
        "MAX_ITEMS": "30",
        "LONG_METHOD_LINES": "60",
        "WEIGHT_COMPLEXITY": "0.5",
        "WEIGHT_COVERAGE": "0.25",
        "WEIGHT_BUSINESS": "0.15",
        "WEIGHT_FREQUENCY": "0.1"
      }
    }
  }
}
```

---

## 配置参数详解

### 复杂度分析参数

#### COMPLEXITY_THRESHOLD
- **说明**: 圈复杂度阈值，超过此值的方法会被标记为复杂方法
- **默认值**: `10`
- **推荐值**: 10-15
- **示例**: `export COMPLEXITY_THRESHOLD=15`

#### MAX_ITEMS
- **说明**: 返回的最大债务项数量
- **默认值**: `20`
- **推荐值**: 10-50
- **示例**: `export MAX_ITEMS=30`

---

### 代码坏味检测参数

#### LONG_METHOD_LINES
- **说明**: 长方法的行数阈值，超过此值的方法会被标记为长方法
- **默认值**: `50`
- **推荐值**: 40-80
- **示例**: `export LONG_METHOD_LINES=60`

#### GOD_CLASS_METHODS
- **说明**: 上帝类的方法数阈值，超过此值的类会被标记为上帝类
- **默认值**: `20`
- **推荐值**: 15-30
- **示例**: `export GOD_CLASS_METHODS=25`

#### GOD_CLASS_LINES
- **说明**: 上帝类的代码行数阈值，超过此值的类会被标记为上帝类
- **默认值**: `500`
- **推荐值**: 300-800
- **示例**: `export GOD_CLASS_LINES=600`

#### DUPLICATE_BLOCK_SIZE
- **说明**: 重复代码块的行数阈值，连续多少行相同被视为重复
- **默认值**: `10`
- **推荐值**: 6-15
- **示例**: `export DUPLICATE_BLOCK_SIZE=12`

---

### 债务指数权重

债务指数计算公式：
```
debt_index =
  WEIGHT_COMPLEXITY × normalized(complexity) +
  WEIGHT_COVERAGE × (1 - coverage) +
  WEIGHT_BUSINESS × normalized(business_impact) +
  WEIGHT_FREQUENCY × normalized(modification_frequency)
```

#### WEIGHT_COMPLEXITY
- **说明**: 复杂度权重
- **默认值**: `0.4` (40%)
- **范围**: 0.0-1.0
- **推荐**: 如果项目复杂度高，建议提高此权重

#### WEIGHT_COVERAGE
- **说明**: 测试覆盖率权重
- **默认值**: `0.3` (30%)
- **范围**: 0.0-1.0
- **推荐**: 如果项目重视测试，建议提高此权重

#### WEIGHT_BUSINESS
- **说明**: 业务影响权重
- **默认值**: `0.2` (20%)
- **范围**: 0.0-1.0
- **推荐**: 如果核心业务模块多，建议提高此权重

#### WEIGHT_FREQUENCY
- **说明**: 修改频率权重
- **默认值**: `0.1` (10%)
- **范围**: 0.0-1.0
- **推荐**: 如果项目活跃度高，建议提高此权重

**权重配置示例**：

```bash
# 场景1: 关注代码质量
export WEIGHT_COMPLEXITY=0.5
export WEIGHT_COVERAGE=0.35
export WEIGHT_BUSINESS=0.1
export WEIGHT_FREQUENCY=0.05

# 场景2: 关注业务稳定性
export WEIGHT_COMPLEXITY=0.3
export WEIGHT_COVERAGE=0.2
export WEIGHT_BUSINESS=0.4
export WEIGHT_FREQUENCY=0.1

# 场景3: 均衡考虑
export WEIGHT_COMPLEXITY=0.4
export WEIGHT_COVERAGE=0.3
export WEIGHT_BUSINESS=0.2
export WEIGHT_FREQUENCY=0.1
```

---

### 性能参数

#### ANALYSIS_TIMEOUT
- **说明**: 分析超时时间（秒）
- **默认值**: `300` (5分钟)
- **推荐值**: 60-600
- **示例**: `export ANALYSIS_TIMEOUT=600`

#### MAX_FILE_SIZE
- **说明**: 最大文件大小（字节），超过此大小的文件会被跳过
- **默认值**: `1048576` (1MB)
- **推荐值**: 524288-5242880 (512KB-5MB)
- **示例**: `export MAX_FILE_SIZE=2097152`

---

### 其他参数

#### EXCLUDE_PATTERNS
- **说明**: 排除的文件模式（逗号分隔）
- **默认值**: `test*,tests*,*Test*,*test*`
- **示例**: `export EXCLUDE_PATTERNS="test*,tests*,*Test*,*test*,vendor/*"`

#### ENABLE_AI_SUGGESTIONS
- **说明**: 是否启用 AI 重构建议
- **默认值**: `false`
- **注意**: 需要 `ANTHROPIC_API_KEY` 环境变量
- **示例**: `export ENABLE_AI_SUGGESTIONS=true`

---

## 使用示例

### 示例 1: 宽松配置（减少误报）

```bash
export COMPLEXITY_THRESHOLD=15        # 提高复杂度阈值
export LONG_METHOD_LINES=60           # 提高长方法阈值
export GOD_CLASS_METHODS=25           # 提高上帝类方法数
export MAX_ITEMS=30                   # 返回更多结果
```

### 示例 2: 严格配置（提高检出率）

```bash
export COMPLEXITY_THRESHOLD=8         # 降低复杂度阈值
export LONG_METHOD_LINES=40           # 降低长方法阈值
export GOD_CLASS_METHODS=15           # 降低上帝类方法数
export MAX_ITEMS=50                   # 返回更多结果
```

### 示例 3: 项目特定配置

```bash
# 针对大型遗留项目的配置
export COMPLEXITY_THRESHOLD=20        # 遗留代码复杂度高，放宽标准
export LONG_METHOD_LINES=80           # 允许较长的方法
export GOD_CLASS_METHODS=30           # 允许较大的类
export MAX_ITEMS=100                  # 显示更多问题
export WEIGHT_BUSINESS=0.4            # 更关注业务影响
export WEIGHT_COMPLEXITY=0.3          # 适度关注复杂度
```

---

## 配置验证

运行以下命令验证配置是否生效：

```python
from config import get_config

config = get_config()
print("当前配置:")
print(f"  复杂度阈值: {config.get('COMPLEXITY_THRESHOLD')}")
print(f"  最大返回项数: {config.get('MAX_ITEMS')}")
print(f"  长方法行数: {config.get('LONG_METHOD_LINES')}")
print(f"  债务指数权重: {config.get_weights()}")
```

---

## 配置优先级

配置加载优先级（从高到低）：

1. **代码中的显式参数** - 调用函数时传入的参数
2. **环境变量** - 系统环境变量或 .env 文件
3. **默认值** - 代码中定义的默认值

---

## 最佳实践

1. **开发环境**: 使用宽松配置，减少干扰
2. **CI/CD**: 使用严格配置，确保质量
3. **遗留项目**: 使用中等配置，渐进式改进
4. **新项目**: 使用严格配置，防止技术债务积累

---

## 故障排查

### 配置未生效

检查环境变量是否正确设置：

```bash
# Linux/macOS
echo $COMPLEXITY_THRESHOLD

# 或者运行 Python
python3 -c "import os; print(os.getenv('COMPLEXITY_THRESHOLD'))"
```

### 权重总和不等于 1.0

权重会自动归一化，总和不等于 1.0 也能正常工作：

```python
# 实际权重会按比例调整
actual_weight = user_weight / sum(all_weights)
```

---

## 相关文档

- [README.md](README.md) - 项目介绍
- [docs/TECHNICAL_DOCUMENTATION.md](docs/TECHNICAL_DOCUMENTATION.md) - 技术文档
- [debt/Tech-Debt-MCP优化建议.md](debt/Tech-Debt-MCP优化建议.md) - 优化建议