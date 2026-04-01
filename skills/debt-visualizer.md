---
name: debt-visualizer
description: 量化技术债务并生成治理路线图，支持多语言、SonarQube集成、增量分析、高级坏味检测、多格式输出和可视化报告
---

# Tech Debt Visualizer

## 工作流

### 步骤 0: 数据源选择
询问用户："请选择技术债务数据来源：1) 本地分析（复杂度+坏味+覆盖率） 2) SonarQube"
若选择 SonarQube，调用 `get_sonarqube_metrics_tool` 获取数据，并直接进入优先级排序。

### 步骤 1: 收集债务项（本地模式）
询问用户分析模式：
- **全量分析**: 分析整个项目
- **增量分析**: 只分析自上次以来的变更文件（需提供 since_commit，如 `HEAD~5`）

调用工具：
- `compute_complexity_tool`（传入 since_commit）
- `detect_code_smells_tool`（基础坏味检测）
- `detect_advanced_smells_tool`（高级坏味检测：深层嵌套、魔法数字、长参数列表等）
- 若用户提供 JaCoCo 报告，调用 `calculate_coverage_tool`

### 步骤 2: 补充业务影响
- 自动从 Git 历史获取文件修改频率（调用内部 `get_modification_frequency`）。
- 询问用户业务核心模块，或使用自动识别结果。

### 步骤 3: 优先级排序 + AI 建议
- 调用 `prioritize_debt`，设置 `generate_suggestions=True`。
- 展示 Top 10 高优先级债务项表格，包含 AI 生成的重构建议。

### 步骤 4: 生成治理路线图
- 询问 Sprint 容量和周期。
- 调用 `generate_roadmap_tool` 输出计划。

### 步骤 5: 输出与可视化
询问用户输出格式：
- **JSON**: 结构化数据
- **Markdown**: 文档格式
- **HTML**: 网页格式
- **CSV**: 表格数据
- **可视化仪表板**: 交互式图表报告

调用相应工具：
- `format_output_tool`（JSON/Markdown/HTML/CSV）
- `generate_dashboard_tool`（可视化仪表板）

### 步骤 6: 导出与后续
- 询问是否导出 Jira CSV。
- 提示增量分析可在 CI 中使用。
- 状态持久化支持：下次分析可基于上次结果进行增量分析。

## 可用工具

### 核心分析工具
- `compute_complexity` - 计算代码复杂度（支持增量分析）
- `detect_code_smells` - 检测基础代码坏味（长方法、上帝类、重复代码）
- `detect_advanced_smells` - 检测高级代码坏味（深层嵌套、魔法数字、长参数列表、数据类、过度注释）
- `calculate_coverage` - 解析 JaCoCo 测试覆盖率报告
- `get_sonarqube_metrics` - 从 SonarQube 获取度量数据

### 优先级与规划工具
- `prioritize_debt` - 债务优先级排序（支持生成 AI 建议）
- `generate_roadmap` - 生成治理路线图
- `generate_refactor_suggestions` - 生成 AI 重构建议

### 输出与可视化工具
- `format_output` - 格式化输出（JSON/Markdown/HTML/CSV）
- `generate_dashboard` - 生成可视化仪表板（HTML 报告）

### 增量分析工具
- `run_incremental_analysis` - 运行增量分析（基于上次状态）
- `run_full_analysis` - 运行全量分析并保存状态

## 高级功能

### 1. 增量分析
- 自动保存分析状态到 `.tech-debt-state.json`
- 支持基于 Git commit 的增量分析
- 只分析变更文件，提升性能

### 2. 高级代码坏味检测
- **深层嵌套**: 检测嵌套深度 > 4 的代码
- **魔法数字**: 检测硬编码的数字常量
- **长参数列表**: 检测参数数量 > 5 的方法
- **数据类**: 检测只有 getter/setter 的类
- **过度注释**: 检测注释占比 > 30% 的文件

### 3. 多格式输出
- 支持 JSON、Markdown、HTML、CSV、Excel 格式
- 可自定义输出模板
- 支持批量导出

### 4. 可视化仪表板
- 交互式图表（类型分布、复杂度分布）
- 统计卡片（总债务项、高优先级、平均复杂度、总修改次数）
- Top 10 债务项表格
- 支持导出 HTML 文件

## 环境变量配置

可通过环境变量自定义检测参数：

```bash
# 复杂度阈值
export MAX_CYCLOMATIC_COMPLEXITY=15
export MAX_LINES_OF_CODE=100

# 代码坏味检测阈值
export MAX_NESTING_DEPTH=4
export MAX_PARAMETER_COUNT=5
export MIN_COMMENT_RATIO=0.1
export MAX_COMMENT_RATIO=0.3

# 分析范围
export MAX_FILE_SIZE=500000
export SUPPORTED_EXTENSIONS=.java,.py,.js,.ts,.go,.c,.cpp

# 输出配置
export MAX_ITEMS=20
export OUTPUT_FORMAT=json

# Git 分析
export SINCE_COMMIT=HEAD~10
```

## 使用示例

### 示例 1: 快速分析项目
```
用户: 分析这个项目的技术债务
助手: 我将使用 Tech Debt Visualizer 来分析项目的技术债务。

[调用工具执行分析]

发现 15 个高复杂度方法，8 个代码坏味问题。
建议优先处理以下 3 个高优先级债务项...
```

### 示例 2: 增量分析
```
用户: 分析最近 5 个 commit 的技术债务变化
助手: 我将进行增量分析，只分析最近 5 个 commit 的变更文件。

[调用 compute_complexity(since_commit='HEAD~5')]

发现 3 个变更文件中有 5 个新的技术债务项...
```

### 示例 3: 生成可视化报告
```
用户: 生成一个可视化的技术债务报告
助手: 我将生成一个 HTML 可视化仪表板。

[调用 generate_dashboard]

报告已生成: dashboard.html
包含：统计卡片、图表、Top 10 债务项表格
```

## 注意事项

1. **增量分析**: 首次运行会进行全量分析并保存状态，后续可基于状态进行增量分析
2. **高级坏味检测**: 需要安装 `javalang` 库以支持 Java AST 解析
3. **可视化仪表板**: 需要网络连接以加载 Chart.js 库
4. **性能**: 大项目（>1000 文件）建议使用增量分析模式