## 案例：技术债务量化与治理路线图（Debt Visualizer）

### 业务场景

团队需要客观评估技术债务，制定量化指标和治理计划。

### 使用 Claude Code 的深度方案

#### MCP Server 设计

text

```
名称：tech-debt
工具：
1. compute_complexity(project_path) → 使用 CKJM 或 SonarQube API 获取圈复杂度、认知复杂度
2. detect_code_smells(source_files) → 基于规则库（如重复代码、长方法、上帝类）进行检测
3. calculate_coverage(test_reports) → 从 JaCoCo 报告获取测试覆盖率
4. prioritize_debt(metrics, business_impact) → 按业务重要性排序债务项
5. generate_roadmap(prioritized_list, sprint_capacity) → 生成迭代计划，可导出 Jira CSV
```



#### 实现细节

- **指标聚合**：每个类/方法打分（复杂度权重 + 测试覆盖率权重 + 业务影响权重），形成债务指数。
- **业务影响**：通过 MCP 从 Git 历史获取文件修改频率，修改频繁的类业务影响大，应优先重构。
- **路线图生成**：根据团队迭代速度（如每 sprint 能重构 3 个类）自动排期。

#### Skill 工作流

markdown

```
## Skill: debt-visualizer

1. 调用 compute_complexity 和 detect_code_smells，生成债务清单。
2. 调用 calculate_coverage，标记低覆盖率的债务项。
3. 询问用户：业务核心模块是哪些？（或从 Git 日志自动识别）
4. 调用 prioritize_debt，输出 Top 10 高优先级债务项（表格形式）。
5. 调用 generate_roadmap，生成按 sprint 划分的治理计划。
6. 输出报告（Markdown），并可选导出 Jira 导入文件。
```



#### 上下文管理

- 全量扫描可能产生数百条债务项，MCP 返回**前 20 项**，其余以“更多请查看完整报告”替代。
- Skill 引导用户通过“增加过滤条件”逐步缩小范围（如只关注复杂度>15 的方法）。

#### 挑战与解决

- **挑战**：债务量化标准难以统一。
  **解决**：Skill 允许用户自定义权重，或使用行业基准（如复杂度>10 为高债务）。
- **挑战**：重构计划可能与业务需求冲突。
  **解决**：输出时可选择“非侵入式”重构（如先加测试再重构）与“阻断式”重构两种方案。