#!/bin/bash
# 构建 tech-debt-mcp 可执行文件

set -e

echo "=== Tech-Debt-MCP 构建脚本 ==="

# 检查 Python 版本
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python 版本: $PYTHON_VERSION}"

# 安装构建依赖
echo ""
echo "步骤 1/3: 安装构建依赖..."
pip install pyinstaller -q

# 安装项目依赖
echo "步骤 2/3: 安装项目依赖..."
pip install -r requirements.txt -q

# 构建
echo "步骤 3/3: 构建可执行文件..."
pyinstaller tech-debt-mcp.spec --clean

echo ""
echo "=== 构建完成 ==="
echo "可执行文件位置: dist/tech-debt-mcp"
echo ""
echo "使用方法 - 更新 MCP 配置:"
echo ""
cat << 'EOF'
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
EOF