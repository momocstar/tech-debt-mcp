# Tech-Debt-MCP 故障排查指南

本文档列出了常见问题及其解决方案。

---

## 目录

1. [安装问题](#安装问题)
2. [配置问题](#配置问题)
3. [运行时错误](#运行时错误)
4. [性能问题](#性能问题)
5. [输出问题](#输出问题)
6. [环境验证](#环境验证)

---

## 安装问题

### 问题 1: Python 版本不兼容

**症状**:
```
SyntaxError: invalid syntax
```

**原因**: Python 版本低于 3.12

**解决方案**:
```bash
# 检查 Python 版本
python --version

# 升级 Python（macOS）
brew install python@3.12

# 使用 Python 3.12 运行
python3.12 -m pip install -r requirements.txt
```

---

### 问题 2: 依赖安装失败

**症状**:
```
ERROR: Could not find a version that satisfies the requirement
```

**原因**: pip 版本过低或网络问题

**解决方案**:
```bash
# 升级 pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或逐个安装
pip install mcp lizard radon gitpython python-sonarqube-api requests javalang
```

---

### 问题 3: lizard 安装失败

**症状**:
```
Building wheel for lizard: error
```

**原因**: 缺少编译工具

**解决方案**:
```bash
# macOS
xcode-select --install

# Linux (Ubuntu/Debian)
sudo apt-get install build-essential

# 重新安装
pip install lizard --no-cache-dir
```

---

## 配置问题

### 问题 4: Skill 无法识别

**症状**:
```
Unknown skill: debt-visualizer
```

**原因**: Skill 配置路径错误

**解决方案**:

1. 检查配置文件：
```bash
cat ~/.claude/settings.json
```

2. 确保 skills 配置正确：
```json
{
  "skills": {
    "paths": ["/Users/momoc/Desktop/skill/tech-debt-mcp/skills"]
  }
}
```

3. 重启 Claude Code：
   - 退出 Claude Code
   - 重新启动

---

### 问题 5: MCP Server 无法启动

**症状**:
```
Failed to connect to tech-debt MCP server
```

**原因**: 可执行文件不存在或权限不足

**解决方案**:

1. 检查可执行文件：
```bash
ls -la /Users/momoc/Desktop/skill/tech-debt-mcp/dist/tech-debt-mcp
```

2. 如果不存在，构建项目：
```bash
cd /Users/momoc/Desktop/skill/tech-debt-mcp
./build.sh
```

3. 或使用 Python 运行：
```json
{
  "mcpServers": {
    "tech-debt": {
      "command": "python",
      "args": ["/Users/momoc/Desktop/skill/tech-debt-mcp/server.py"],
      "env": {
        "CKJM_JAR": "/Users/momoc/Desktop/skill/tech-debt-mcp/ckjm-1.9.jar"
      }
    }
  }
}
```

---

### 问题 6: 环境变量未生效

**症状**: 配置参数未按预期工作

**原因**: 环境变量未正确设置

**解决方案**:

1. 检查环境变量：
```bash
env | grep COMPLEXITY_THRESHOLD
```

2. 在 .mcp.json 中设置：
```json
{
  "mcpServers": {
    "tech-debt": {
      "env": {
        "COMPLEXITY_THRESHOLD": "15",
        "LONG_METHOD_LINES": "60"
      }
    }
  }
}
```

3. 或在 shell 中设置：
```bash
export COMPLEXITY_THRESHOLD=15
export LONG_METHOD_LINES=60
```

---

## 运行时错误

### 问题 7: 项目路径不存在

**症状**:
```
ProjectNotFoundError: 项目路径不存在
```

**解决方案**:

1. 检查路径是否存在：
```bash
ls -la /path/to/project
```

2. 使用绝对路径：
```bash
# 正确 ✅
/Users/username/projects/my-app

# 错误 ❌
~/projects/my-app
../my-app
```

3. 检查路径权限：
```bash
ls -la /path/to/project
```

---

### 问题 8: 未找到源代码文件

**症状**:
```
InvalidProjectStructureError: 项目结构无效，未找到源代码
```

**原因**: 项目不包含支持的源代码文件

**解决方案**:

1. 确认项目包含源代码：
```bash
find /path/to/project -name "*.java" -o -name "*.py" | head
```

2. 检查文件扩展名：
   - Java: `.java`
   - Python: `.py`
   - JavaScript: `.js`
   - TypeScript: `.ts`
   - Go: `.go`
   - C/C++: `.c`, `.cpp`, `.h`

---

### 问题 9: Git 增量分析失败

**症状**:
```
GitRepositoryRequiredError: 增量分析需要 Git 仓库
```

**原因**: 项目不是 Git 仓库

**解决方案**:

1. 初始化 Git 仓库：
```bash
cd /path/to/project
git init
git add .
git commit -m "Initial commit"
```

2. 或使用全量分析：
```bash
# 不指定 since_commit 参数
python server.py compute_complexity --project_path /path/to/project
```

---

### 问题 10: 分析超时

**症状**:
```
AnalysisTimeoutError: 分析超时，超过 300 秒
```

**原因**: 项目过大或系统资源不足

**解决方案**:

1. 增加超时时间：
```bash
export ANALYSIS_TIMEOUT=600  # 10 分钟
```

2. 使用增量分析：
```bash
# 只分析最近 10 次提交
python server.py compute_complexity --project_path /path/to/project --since_commit HEAD~10
```

3. 减少分析文件：
```bash
# 排除测试文件
export EXCLUDE_PATTERNS="test*,tests*,*Test*"
```

---

## 性能问题

### 问题 11: 分析速度慢

**症状**: 分析大项目耗时过长

**解决方案**:

1. 使用增量分析：
```bash
# 只分析变更文件
--since_commit HEAD~5
```

2. 调整参数：
```bash
# 减少返回项数
export MAX_ITEMS=10

# 提高复杂度阈值
export COMPLEXITY_THRESHOLD=15

# 减小最大文件大小
export MAX_FILE_SIZE=524288  # 512KB
```

3. 并行分析（未来版本支持）

---

### 问题 12: 内存占用高

**症状**: 分析过程中内存飙升

**解决方案**:

1. 减少分析的文件数量：
```bash
export MAX_FILE_SIZE=524288  # 512KB
```

2. 排除大文件：
```bash
export EXCLUDE_PATTERNS="vendor/*,node_modules/*,build/*"
```

3. 分批分析：
```bash
# 分析单个模块
python server.py compute_complexity --project_path /path/to/project/module1
```

---

## 输出问题

### 问题 13: 代码坏味检测结果不准确

**症状**: 检测到的都是 `enum`, `static` 等关键字

**原因**: javalang 库未安装

**解决方案**:

1. 安装 javalang：
```bash
pip install javalang>=0.13.0
```

2. 验证安装：
```python
python -c "import javalang; print('✅ javalang 已安装')"
```

3. 重新运行分析

---

### 问题 14: JSON 输出格式错误

**症状**:
```
JSONDecodeError: Expecting value
```

**原因**: 输出被截断或包含非 JSON 内容

**解决方案**:

1. 检查日志输出：
```bash
python server.py compute_complexity --project_path /path/to/project 2>&1 | grep -v "^[^{\[]"
```

2. 重定向错误输出：
```bash
python server.py compute_complexity --project_path /path/to/project 2>/dev/null
```

---

### 问题 15: Jira CSV 导入失败

**症状**: Jira 导入 CSV 报错

**解决方案**:

1. 检查 CSV 编码：
```bash
file /tmp/tech_debt_jira_import.csv
```

2. 转换编码：
```bash
iconv -f UTF-8 -t UTF-8 /tmp/tech_debt_jira_import.csv > output.csv
```

3. 在 Jira 中映射字段：
   - Project Key → 项目键
   - Issue Type → 问题类型
   - Summary → 摘要
   - Priority → 优先级

---

## 环境验证

### 自动验证

运行验证脚本：

```bash
python validation.py
```

**预期输出**:
```
================================================================================
Tech-Debt-MCP 环境验证
================================================================================

✅ 环境验证通过

💡 建议:
  - javalang 未安装，代码坏味检测将使用后备方案（准确度较低）
  - 建议安装: pip install javalang>=0.13.0

================================================================================
```

---

### 手动验证

#### 1. 验证 Python 版本
```bash
python --version  # 应为 3.12+
```

#### 2. 验证依赖
```bash
python -c "
import sys
modules = ['mcp', 'lizard', 'radon', 'git', 'requests']
for mod in modules:
    try:
        __import__(mod)
        print(f'✅ {mod}')
    except ImportError:
        print(f'❌ {mod}')
"
```

#### 3. 验证配置
```bash
# 检查 MCP 配置
cat ~/.claude/settings.json | grep -A 5 tech-debt

# 检查环境变量
env | grep -E "(COMPLEXITY|WEIGHT|THRESHOLD)"
```

#### 4. 验证项目结构
```bash
# 检查源代码文件
find /path/to/project -name "*.java" | wc -l

# 检查 Git 仓库
cd /path/to/project && git status
```

---

## 获取帮助

### 日志级别

启用详细日志：

```bash
export LOG_LEVEL=DEBUG
python server.py compute_complexity --project_path /path/to/project
```

### 报告问题

如果问题仍未解决，请提供以下信息：

1. **环境信息**:
   ```bash
   python --version
   pip list | grep -E "(mcp|lizard|radon|javalang)"
   ```

2. **配置信息**:
   ```bash
   cat ~/.claude/settings.json
   ```

3. **错误信息**: 完整的错误堆栈

4. **重现步骤**: 详细的操作步骤

---

## 常用命令速查

```bash
# 验证环境
python validation.py

# 测试配置
python -c "from config import get_config; print(get_config())"

# 运行分析
python server.py compute_complexity --project_path /path/to/project

# 增量分析
python server.py compute_complexity --project_path /path/to/project --since_commit HEAD~10

# 检测代码坏味
python server.py detect_code_smells --project_path /path/to/project

# 生成路线图
python server.py generate_roadmap --items_json '[...]' --sprint_capacity 5
```

---

**更新日期**: 2026-04-01
**版本**: v1.1