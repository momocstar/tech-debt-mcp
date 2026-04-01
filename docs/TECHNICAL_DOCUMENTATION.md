# Tech-Debt-MCP 技术文档与使用教程

## 一、项目概述

**Tech-Debt-MCP** 是一个基于 MCP (Model Context Protocol) 的技术债务量化与治理工具。它能够：

- 自动扫描项目代码，计算复杂度指标
- 检测代码坏味（长方法、上帝类、重复代码）
- 解析测试覆盖率报告
- 结合 Git 历史分析业务影响
- 生成 AI 重构建议
- 输出按 Sprint 规划的治理路线图

## 二、架构设计

```
tech-debt-mcp/
├── server.py              # MCP Server 入口，注册所有工具
├── models.py              # 数据模型定义
├── utils.py               # 工具函数（语言检测等）
├── analyzers/             # 分析器模块
│   ├── git_analyzer.py    # Git 历史分析（修改频率、变更文件）
│   ├── generic_lizard.py  # 多语言复杂度分析
│   ├── python_radon.py    # Python 专用分析
│   └── java_ckjm.py       # Java CKJM 分析器
├── tools/                 # MCP 工具实现
│   ├── complexity.py      # compute_complexity
│   ├── smells.py          # detect_code_smells
│   ├── coverage.py        # calculate_coverage
│   ├── prioritize.py      # prioritize_debt
│   ├── roadmap.py         # generate_roadmap
│   ├── sonarqube.py       # get_sonarqube_metrics
│   └── ai_suggestions.py  # generate_refactor_suggestions
├── skill/
│   └── debt-visualizer.md # Claude Code Skill 工作流
├── ckjm-1.9.jar           # Java CKJM 工具
└── mcp.config.example     # MCP 配置示例
```

## 三、核心数据模型

### 3.1 DebtType（债务类型枚举）

| 类型 | 说明 |
|------|------|
| `COMPLEX_METHOD` | 复杂方法（圈复杂度过高） |
| `LONG_METHOD` | 长方法（超过50行） |
| `GOD_CLASS` | 上帝类（方法数>20或行数>500） |
| `DUPLICATE_CODE` | 重复代码块 |
| `LOW_COVERAGE` | 低测试覆盖率（<70%） |

### 3.2 DebtItem（债务项）

```python
@dataclass
class DebtItem:
    id: str                    # 唯一标识
    type: DebtType             # 债务类型
    file_path: str             # 文件路径
    entity_name: str           # 类名或方法名
    start_line: int            # 起始行
    end_line: int              # 结束行
    complexity: float          # 复杂度
    coverage: float            # 覆盖率
    modification_frequency: int # Git修改频率
    business_impact: float     # 业务影响权重
    custom_notes: str          # 自定义备注
```

### 3.3 债务指数计算公式

```python
debt_index = (
    weights['complexity'] * norm(complexity, 20) +
    weights['coverage'] * (1 - coverage) +
    weights['business'] * norm(business_impact, 5) +
    weights['frequency'] * norm(modification_frequency, 30)
)
```

默认权重：复杂度 40%、覆盖率 30%、业务影响 20%、修改频率 10%

## 四、MCP 工具清单

| 工具名 | 功能 | 必需参数 | 可选参数 |
|--------|------|----------|----------|
| `compute_complexity` | 计算代码复杂度 | `project_path` | `max_items`, `since_commit` |
| `detect_code_smells` | 检测代码坏味 | `project_path` | `max_items` |
| `calculate_coverage` | 解析 JaCoCo 覆盖率 | `report_path` | `max_items` |
| `prioritize_debt` | 债务优先级排序 | `project_path`, `items_json` | `weights_json`, `business_tags_json`, `generate_suggestions` |
| `generate_roadmap` | 生成治理路线图 | `prioritized_items_json`, `sprint_capacity` | `sprint_days`, `start_date` |
| `get_sonarqube_metrics` | 从 SonarQube 获取数据 | `project_key` | `base_url`, `token` |
| `generate_refactor_suggestions` | 生成 AI 重构建议 | `items_json` | - |

## 五、安装与配置

### 5.1 环境要求

- Python 3.12+
- Java Runtime（用于 CKJM）
- Git

### 5.2 安装依赖

```bash
cd /path/to/tech-debt-mcp
pip install -r requirements.txt
```

依赖包：
- `mcp` - MCP 协议库
- `lizard` - 多语言复杂度分析
- `radon` - Python 复杂度分析
- `gitpython` - Git 操作
- `python-sonarqube-api` - SonarQube API 客户端
- `requests` - HTTP 请求

### 5.3 配置 MCP Server

编辑 Claude Code 配置文件（如 `~/.claude/settings.json`）：

```json
{
  "mcpServers": {
    "tech-debt": {
      "command": "python",
      "args": ["/path/to/tech-debt-mcp/server.py"],
      "env": {
        "CKJM_JAR": "/path/to/tech-debt-mcp/ckjm-1.9.jar",
        "SONARQUBE_URL": "http://sonar.example.com",
        "SONARQUBE_TOKEN": "your_token_here",
        "ANTHROPIC_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## 六、使用教程

### 6.1 基本工作流

#### 步骤 1：计算代码复杂度

```json
{
  "project_path": "/path/to/your/project",
  "max_items": 20
}
```

增量分析（只分析最近5次提交的变更）：

```json
{
  "project_path": "/path/to/your/project",
  "since_commit": "HEAD~5"
}
```

#### 步骤 2：检测代码坏味

```json
{
  "project_path": "/path/to/your/project",
  "max_items": 20
}
```

#### 步骤 3：分析测试覆盖率

```json
{
  "report_path": "/path/to/jacoco.xml",
  "max_items": 20
}
```

#### 步骤 4：优先级排序

```json
{
  "project_path": "/path/to/your/project",
  "items_json": "[{\"id\":\"...\", \"type\":\"complex_method\", ...}]",
  "weights_json": "{\"complexity\": 0.5, \"coverage\": 0.3, \"business\": 0.1, \"frequency\": 0.1}",
  "generate_suggestions": true
}
```

#### 步骤 5：生成治理路线图

```json
{
  "prioritized_items_json": "[{\"id\":\"...\", \"debt_score\": 0.85, ...}]",
  "sprint_capacity": 5,
  "sprint_days": 14,
  "start_date": "2026-04-01"
}
```

### 6.2 使用 SonarQube 数据源

```json
{
  "project_key": "my-project",
  "base_url": "http://sonar.example.com",
  "token": "your_token"
}
```

### 6.3 在 Claude Code 中使用 Skill

项目已内置 `debt-visualizer` Skill，Claude Code 会自动引导以下流程：

```
1. 选择数据源（本地分析 或 SonarQube）
2. 是否增量分析
3. 补充业务影响信息
4. 生成 Top 10 优先级列表 + AI 建议
5. 生成 Sprint 路线图
6. 可选导出 Jira CSV
```

### 6.4 输出示例

**复杂度分析结果：**

```json
{
  "items": [
    {
      "id": "/src/main.py:process_data",
      "type": "complex_method",
      "file_path": "/src/main.py",
      "entity_name": "process_data",
      "complexity": 15,
      "start_line": 42,
      "end_line": 120
    }
  ],
  "total_count": "more than 20",
  "truncated": true,
  "message": "返回前20个高复杂度项。"
}
```

**治理路线图：**

```json
{
  "sprints": [
    {
      "name": "Sprint 1",
      "start": "2026-04-01",
      "end": "2026-04-15",
      "items": [
        {"id": "...", "entity_name": "OrderService.processOrder", "debt_score": 0.92},
        {"id": "...", "entity_name": "PaymentService.validate", "debt_score": 0.87}
      ]
    },
    {
      "name": "Sprint 2",
      "start": "2026-04-15",
      "end": "2026-04-29",
      "items": [...]
    }
  ]
}
```

## 七、扩展与自定义

### 7.1 自定义权重

通过 `weights_json` 参数调整债务指数计算：

```json
{
  "complexity": 0.5,
  "coverage": 0.2,
  "business": 0.2,
  "frequency": 0.1
}
```

### 7.2 添加业务标签

```json
{
  "/src/order/OrderService.java": 5.0,
  "/src/payment/PaymentService.java": 4.5
}
```

### 7.3 支持的语言

| 语言 | 分析器 |
|------|--------|
| Java | Lizard / CKJM |
| Python | Lizard / Radon |
| JavaScript | Lizard |
| TypeScript | Lizard |
| Go | Lizard |
| C/C++ | Lizard |

## 八、注意事项

1. **上下文管理**：MCP 默认返回前 20 项，避免上下文过载
2. **增量分析**：在 CI/CD 中使用 `since_commit` 参数只分析变更文件
3. **API Key**：AI 建议功能需要配置 `ANTHROPIC_API_KEY`
4. **SonarQube**：需提前配置服务器 URL 和访问令牌

## 九、工具详细说明

### 9.1 compute_complexity

计算项目代码复杂度，支持增量分析。

**参数说明：**
- `project_path` (必需): 项目根目录路径
- `max_items` (可选): 返回的最大项数，默认20
- `since_commit` (可选): 只分析自该commit以来的变更文件，如 `HEAD~5`

**工作原理：**
1. 自动检测项目主要语言
2. 根据语言选择合适的分析器（Lizard/Radon/CKJM）
3. 如指定 `since_commit`，只分析变更文件
4. 返回复杂度超过阈值（>10）的方法列表

### 9.2 detect_code_smells

检测代码坏味，包括长方法、上帝类、重复代码。

**检测规则：**
- 长方法：方法行数 > 50
- 上帝类：类内方法数 > 20
- 重复代码：连续10行代码块在多处出现

### 9.3 calculate_coverage

解析 JaCoCo XML 测试覆盖率报告。

**参数说明：**
- `report_path` (必需): JaCoCo XML 报告路径
- `max_items` (可选): 返回的最大项数，默认20

**返回：** 覆盖率低于70%的类列表

### 9.4 prioritize_debt

对技术债务项进行优先级排序，并可生成AI建议。

**参数说明：**
- `project_path` (必需): 项目根目录路径
- `items_json` (必需): 债务项JSON字符串（列表）
- `weights_json` (可选): 权重配置
- `business_tags_json` (可选): 业务影响标签
- `generate_suggestions` (可选): 是否生成AI建议

**工作原理：**
1. 从 Git 历史获取文件修改频率
2. 结合复杂度、覆盖率、业务影响计算债务指数
3. 按债务指数降序排列
4. 可选调用 Claude API 生成重构建议

### 9.5 generate_roadmap

根据排序后的债务项生成治理路线图。

**参数说明：**
- `prioritized_items_json` (必需): 排序后的债务项JSON
- `sprint_capacity` (必需): 每个Sprint能处理的项目数
- `sprint_days` (可选): Sprint天数，默认14
- `start_date` (可选): 开始日期 YYYY-MM-DD

### 9.6 get_sonarqube_metrics

从 SonarQube 获取度量数据。

**参数说明：**
- `project_key` (必需): SonarQube项目键
- `base_url` (可选): SonarQube服务器URL，可从环境变量读取
- `token` (可选): 访问令牌，可从环境变量读取

### 9.7 generate_refactor_suggestions

为债务项生成 AI 重构建议。

**参数说明：**
- `items_json` (必需): 债务项JSON列表

**工作原理：**
- 调用 Claude API 为每个债务项生成具体重构建议
- 如未配置 API Key，返回预设的模拟建议

## 十、Skill 工作流详解

`debt-visualizer` Skill 定义了完整的工作流：

### 步骤 0: 数据源选择
询问用户选择数据来源：
1. 本地分析（复杂度+坏味+覆盖率）
2. SonarQube

### 步骤 1: 收集债务项（本地模式）
- 询问是否需要增量分析
- 调用 `compute_complexity` 和 `detect_code_smells`
- 若有 JaCoCo 报告，调用 `calculate_coverage`

### 步骤 2: 补充业务影响
- 自动从 Git 历史获取文件修改频率
- 询问用户业务核心模块

### 步骤 3: 优先级排序 + AI 建议
- 调用 `prioritize_debt`，设置 `generate_suggestions=True`
- 展示 Top 10 高优先级债务项表格

### 步骤 4: 生成治理路线图
- 询问 Sprint 容量和周期
- 调用 `generate_roadmap` 输出计划

### 步骤 5: 导出与后续
- 询问是否导出 Jira CSV
- 提示增量分析可在 CI 中使用