---
name: debt-visualizer
description: 量化技术债务并生成治理路线图，支持多语言、SonarQube集成、增量分析和AI建议
---

# Tech Debt Visualizer

## 工作流

### 步骤 0: 数据源选择
询问用户：“请选择技术债务数据来源：1) 本地分析（复杂度+坏味+覆盖率） 2) SonarQube”
若选择 SonarQube，调用 `get_sonarqube_metrics_tool` 获取数据，并直接进入优先级排序。

### 步骤 1: 收集债务项（本地模式）
- 询问用户是否需要增量分析（提供 since_commit，如 `HEAD~5`）。
- 调用 `compute_complexity_tool`（传入 since_commit）和 `detect_code_smells_tool`。
- 若用户提供 JaCoCo 报告，调用 `calculate_coverage_tool`。

### 步骤 2: 补充业务影响
- 自动从 Git 历史获取文件修改频率（调用内部 `get_modification_frequency`）。
- 询问用户业务核心模块，或使用自动识别结果。

### 步骤 3: 优先级排序 + AI 建议
- 调用 `prioritize_debt`，设置 `generate_suggestions=True`。
- 展示 Top 10 高优先级债务项表格，包含 AI 生成的重构建议。

### 步骤 4: 生成治理路线图
- 询问 Sprint 容量和周期。
- 调用 `generate_roadmap_tool` 输出计划。

### 步骤 5: 导出与后续
- 询问是否导出 Jira CSV。
- 提示增量分析可在 CI 中使用。