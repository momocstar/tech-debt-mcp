# Tech-Debt-MCP

基于 MCP (Model Context Protocol) 的技术债务量化与治理工具。

## 功能特性

- **复杂度分析** - 支持多语言（Java、Python、JavaScript、TypeScript、Go、C/C++）
- **代码坏味检测** - 长方法、上帝类、重复代码
- **覆盖率分析** - 解析 JaCoCo XML 报告
- **Git 历史分析** - 文件修改频率统计
- **优先级排序** - 基于复杂度、覆盖率、业务影响的债务指数计算
- **AI 重构建议** - 调用 Claude API 生成重构建议
- **治理路线图** - 按 Sprint 规划重构计划
- **SonarQube 集成** - 从 SonarQube 获取度量数据
- **增量分析** - 支持只分析指定 commit 后的变更文件

## 快速开始

### 环境要求

- Python 3.12+
- Java Runtime（用于 CKJM）
- Git

### 安装

```bash
# 克隆项目
git clone <repo-url>
cd tech-debt-mcp

# 安装依赖
pip install -r requirements.txt
```

### 构建（可选）

```bash
# macOS/Linux
./build.sh

# Windows
build.bat
```

构建后生成独立可执行文件 `dist/tech-debt-mcp`。

## 配置

### 方式一：使用 Python 直接运行

编辑 `~/.claude/settings.json`：

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

### 方式二：使用可执行文件

```json
{
  "mcpServers": {
    "tech-debt": {
      "command": "/path/to/tech-debt-mcp/dist/tech-debt-mcp",
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

## MCP 工具

| 工具 | 功能 |
|------|------|
| `compute_complexity` | 计算代码复杂度，支持增量分析 |
| `detect_code_smells` | 检测代码坏味（长方法、上帝类、重复代码） |
| `calculate_coverage` | 解析 JaCoCo 覆盖率报告 |
| `prioritize_debt` | 债务优先级排序 |
| `generate_roadmap` | 生成治理路线图 |
| `get_sonarqube_metrics` | 从 SonarQube 获取数据 |
| `generate_refactor_suggestions` | 生成 AI 重构建议 |

## 命令行使用（API 直接调用）

支持通过命令行直接调用，无需 MCP 客户端。

### 计算代码复杂度

```bash
# 基本用法
python server.py complexity /path/to/project

# 限制返回数量
python server.py complexity /path/to/project --max-items 10

# 增量分析（只分析最近5次提交的变更）
python server.py complexity /path/to/project --since-commit HEAD~5
```

### 检测代码坏味

```bash
python server.py smells /path/to/project --max-items 20
```

### 分析测试覆盖率

```bash
python server.py coverage /path/to/jacoco.xml --max-items 20
```

### 优先级排序

```bash
python server.py prioritize /path/to/project \
  --items-json '[{"id":"test","type":"complex_method","file_path":"test.py","entity_name":"func"}]' \
  --weights '{"complexity":0.5,"coverage":0.3,"business":0.1,"frequency":0.1}' \
  --suggestions
```

### 生成治理路线图

```bash
python server.py roadmap \
  --items-json '[{"id":"test","debt_score":0.85}]' \
  --capacity 5 \
  --days 14 \
  --start-date 2026-04-01
```

### 从 SonarQube 获取数据

```bash
python server.py sonarqube my-project \
  --base-url http://sonar.example.com \
  --token your_token
```

### 生成 AI 重构建议

```bash
python server.py suggestions \
  --items-json '[{"id":"test","type":"complex_method","file_path":"test.py"}]'
```

### 输出格式

所有命令输出 JSON 格式，可用 `jq` 处理：

```bash
python server.py complexity . | jq '.items[0]'
```

---

## MCP 调用示例

### 1. 计算代码复杂度

```json
{
  "project_path": "/path/to/project",
  "max_items": 20
}
```

增量分析（只分析最近 5 次提交的变更）：

```json
{
  "project_path": "/path/to/project",
  "since_commit": "HEAD~5"
}
```

### 2. 检测代码坏味

```json
{
  "project_path": "/path/to/project"
}
```

### 3. 分析测试覆盖率

```json
{
  "report_path": "/path/to/jacoco.xml"
}
```

### 4. 优先级排序

```json
{
  "project_path": "/path/to/project",
  "items_json": "[{\"id\":\"...\", \"type\":\"complex_method\", ...}]",
  "generate_suggestions": true
}
```

### 5. 生成治理路线图

```json
{
  "prioritized_items_json": "[{\"id\":\"...\", \"debt_score\": 0.85}]",
  "sprint_capacity": 5,
  "sprint_days": 14,
  "start_date": "2026-04-01"
}
```

## 债务指数计算

```
debt_index = 
  0.4 × normalized(complexity) +
  0.3 × (1 - coverage) +
  0.2 × normalized(business_impact) +
  0.1 × normalized(modification_frequency)
```

默认权重可通过 `weights_json` 参数自定义。

## 债务类型

| 类型 | 说明 | 检测条件 |
|------|------|----------|
| `COMPLEX_METHOD` | 复杂方法 | 圈复杂度 > 10 |
| `LONG_METHOD` | 长方法 | 行数 > 50 |
| `GOD_CLASS` | 上帝类 | 方法数 > 20 |
| `DUPLICATE_CODE` | 重复代码 | 10行代码块重复出现 |
| `LOW_COVERAGE` | 低覆盖率 | 覆盖率 < 70% |

## Skill 使用教程

### 什么是 Skill？

Skill 是 Claude Code 的扩展能力，定义了一套工作流程。本项目内置 `debt-visualizer` Skill，可自动化完成技术债务分析的完整流程。

### 配置 Skill

将 Skill 目录配置到 `~/.claude/settings.json`：

```json
{
  "skills": {
    "paths": ["/Users/momoc/Desktop/skill/tech-debt-mcp/skills"]
  },
  "mcpServers": {
    "tech-debt": {
      "command": "/Users/momoc/Desktop/skill/tech-debt-mcp/dist/tech-debt-mcp",
      "env": {
        "ANTHROPIC_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### 在对话中使用

#### 方式一：直接对话（推荐）

配置完成后，直接在 Claude Code 对话中描述需求即可：

```
帮我分析 /Users/momoc/projects/my-app 的技术债务
```

Claude 会自动调用 MCP 工具和 Skill 完成分析。

#### 方式二：引用 Skill

```
使用 debt-visualizer 分析项目 /path/to/project
```

---

## 使用案例

### 案例 1：快速分析项目技术债务

**对话输入：**

```
分析 /Users/momoc/projects/ecommerce-api 的技术债务情况
```

**Claude 输出：**

```
正在分析项目...

## 技术债务报告

### 高复杂度方法 (Top 5)
| 文件 | 方法 | 复杂度 | 位置 |
|------|------|--------|------|
| OrderService.java | processOrder | 18 | L145-220 |
| PaymentService.java | validatePayment | 15 | L89-156 |
| UserService.java | authenticate | 12 | L34-98 |
| CartService.java | calculateTotal | 11 | L56-89 |
| InventoryService.java | checkStock | 10 | L23-67 |

### 代码坏味检测
- 上帝类：OrderService (23个方法)
- 长方法：PaymentService.validatePayment (67行)
- 重复代码：检测到 3 处重复代码块

### 低覆盖率模块
| 类 | 覆盖率 |
|----|--------|
| OrderService | 45% |
| PaymentService | 52% |

### 优先级建议
1. OrderService.processOrder (债务指数: 0.87)
2. PaymentService.validatePayment (债务指数: 0.72)
3. UserService.authenticate (债务指数: 0.65)
```

---

### 案例 2：增量分析最近变更

**对话输入：**

```
只分析最近5次提交的代码变更，看看引入了哪些技术债务
```

**Claude 输出：**

```
正在分析 HEAD~5 以来的变更文件...

## 增量分析报告

### 变更文件 (8个)
- src/service/OrderService.java (修改 3 次)
- src/controller/OrderController.java (修改 2 次)
- src/model/Order.java (修改 1 次)

### 新增债务
| 文件 | 问题 | 复杂度 |
|------|------|--------|
| OrderService.java | 新增长方法 calculateDiscount | 12 |
| OrderController.java | 复杂度上升 | 8 |

### 建议
优先关注 OrderService.calculateDiscount，建议拆分为多个小方法。
```

---

### 案例 3：生成治理路线图

**对话输入：**

```
根据分析结果，生成未来4个Sprint的技术债务治理计划，每个Sprint处理3个债务项
```

**Claude 输出：**

```
## 技术债务治理路线图

### Sprint 1 (2026-04-01 ~ 2026-04-14)
| 债务项 | 类型 | 债务指数 |
|--------|------|----------|
| OrderService.processOrder | 复杂方法 | 0.87 |
| PaymentService.validatePayment | 复杂方法 | 0.72 |
| OrderService (上帝类) | 上帝类 | 0.68 |

### Sprint 2 (2026-04-15 ~ 2026-04-28)
| 债务项 | 类型 | 债务指数 |
|--------|------|----------|
| UserService.authenticate | 复杂方法 | 0.65 |
| CartService.calculateTotal | 复杂方法 | 0.58 |
| 重复代码块 #1 | 重复代码 | 0.55 |

### Sprint 3 (2026-04-29 ~ 2026-05-12)
...

### Sprint 4 (2026-05-13 ~ 2026-05-26)
...
```

---

### 案例 4：获取 AI 重构建议

**对话输入：**

```
为 OrderService.processOrder 方法生成重构建议
```

**Claude 输出：**

```
## 重构建议：OrderService.processOrder

### 当前问题
- 圈复杂度：18（建议 < 10）
- 方法行数：75行
- 缺少单元测试

### 重构步骤

1. **提取方法：验证订单**
   ```java
   private void validateOrder(Order order) {
       if (order.getItems().isEmpty()) {
           throw new InvalidOrderException("订单不能为空");
       }
       // 其他验证逻辑
   }
   ```

2. **提取方法：计算价格**
   ```java
   private BigDecimal calculateTotalPrice(Order order) {
       return order.getItems().stream()
           .map(Item::getPrice)
           .reduce(BigDecimal.ZERO, BigDecimal::add);
   }
   ```

3. **提取方法：处理支付**
   ```java
   private PaymentResult processPayment(Order order, BigDecimal amount) {
       return paymentService.charge(order.getUserId(), amount);
   }
   ```

4. **添加单元测试**
   - 测试正常流程
   - 测试边界条件
   - 测试异常情况

### 预期效果
- 复杂度降至 6
- 每个方法职责单一
- 测试覆盖率提升至 80%+
```

---

### 案例 5：集成 SonarQube 数据

**对话输入：**

```
从 SonarQube 获取项目 my-project 的技术债务数据
```

**Claude 输出：**

```
正在连接 SonarQube...

## SonarQube 分析报告

### 项目概览
- 代码行数：125,000
- 技术债务：45 天
- 代码异味：328 个
- Bug：12 个
- 漏洞：3 个

### 高优先级问题
| 文件 | 问题 | 严重级别 |
|------|------|----------|
| OrderService.java | 认知复杂过高 | Critical |
| UserRepository.java | SQL 注入风险 | Blocker |
| PaymentUtil.java | 硬编码密码 | Blocker |

### 建议处理顺序
1. 立即处理 Blocker 级别问题
2. 本 Sprint 处理 Critical 级别问题
3. 后续 Sprint 处理 Major 级别问题
```

---

### 案例 6：自定义权重分析

**对话输入：**

```
用自定义权重分析项目，我更关注复杂度和测试覆盖率
权重配置：复杂度 50%，覆盖率 40%，业务影响 5%，修改频率 5%
```

**Claude 输出：**

```
## 自定义权重分析结果

### 权重配置
- 复杂度：50%
- 覆盖率：40%
- 业务影响：5%
- 修改频率：5%

### 重新排序后的债务列表
| 债务项 | 复杂度 | 覆盖率 | 新债务指数 |
|--------|--------|--------|------------|
| OrderService.processOrder | 18 | 35% | 0.91 |
| PaymentService.validate | 15 | 42% | 0.78 |
| InventoryService.check | 8 | 28% | 0.72 |

相比默认权重，覆盖率低的模块排名明显上升。
```

---

## Skill 工作流详解

`debt-visualizer` Skill 执行以下步骤：

1. **数据源选择** - 询问用户：本地分析 或 SonarQube
2. **分析模式** - 全量扫描 或 增量分析（指定 since_commit）
3. **收集债务项** - 调用 compute_complexity + detect_code_smells
4. **补充业务影响** - 从 Git 历史获取修改频率，询问核心模块
5. **优先级排序** - 计算债务指数，按优先级排列
6. **生成建议** - 可选生成 AI 重构建议
7. **输出路线图** - 按 Sprint 规划治理计划
8. **导出** - 可选导出 Jira CSV 格式

## 项目结构

```
tech-debt-mcp/
├── server.py              # MCP Server 入口
├── models.py              # 数据模型
├── utils.py               # 工具函数
├── analyzers/             # 分析器模块
│   ├── git_analyzer.py    # Git 历史分析
│   ├── generic_lizard.py  # 多语言复杂度分析
│   ├── python_radon.py    # Python 分析
│   └── java_ckjm.py       # Java 分析
├── tools/                 # MCP 工具实现
├── skill/                 # Claude Code Skill
├── docs/                  # 文档
├── dist/                  # 构建输出
└── requirements.txt       # 依赖
```

## 支持的语言

| 语言 | 分析器 |
|------|--------|
| Java | Lizard / CKJM |
| Python | Lizard / Radon |
| JavaScript | Lizard |
| TypeScript | Lizard |
| Go | Lizard |
| C/C++ | Lizard |

## 环境变量

| 变量 | 说明 |
|------|------|
| `CKJM_JAR` | CKJM jar 文件路径 |
| `SONARQUBE_URL` | SonarQube 服务器地址 |
| `SONARQUBE_TOKEN` | SonarQube 访问令牌 |
| `ANTHROPIC_API_KEY` | Claude API 密钥（用于 AI 建议） |

## 文档

- [技术文档与使用教程](docs/TECHNICAL_DOCUMENTATION.md)
- [案例介绍](docs/README.md)

## License

MIT